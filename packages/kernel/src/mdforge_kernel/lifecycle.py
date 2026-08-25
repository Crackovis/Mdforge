from __future__ import annotations

from enum import StrEnum
from typing import Any

from mdforge_contracts import EventSink, RuntimeEvent, StructuredError

from .context import BoundRuntimeContext, EventCollector
from .errors import RuntimeActivationError, RuntimeIssue, RuntimeShutdownError
from .registry import CapabilityRegistry
from .resolution import ResolvedGraph


class RuntimeState(StrEnum):
    IDLE = "idle"
    READY = "ready"
    STOPPED = "stopped"
    FAILED_CLEAN = "failed-clean"
    FAILED_DIRTY = "failed-dirty"


class CapabilityState(StrEnum):
    DISCOVERED = "discovered"
    VALIDATED = "validated"
    RESOLVED = "resolved"
    PREPARED = "prepared"
    ACTIVE = "active"
    STOPPING = "stopping"
    STOPPED = "stopped"
    FAILED = "failed"


class CapabilityRuntime:
    def __init__(
        self,
        registry: CapabilityRegistry,
        graph: ResolvedGraph,
        *,
        event_sink: EventSink | None = None,
        configuration: dict[str, dict[str, Any]] | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        self._registry = registry
        self._graph = graph
        self._event_sink = event_sink or EventCollector()
        self._configuration = configuration or {}
        self._metadata = metadata or {}
        self._active: list[str] = []
        self._capability_states = {
            capability_id: CapabilityState.RESOLVED
            for capability_id in graph.selected_capabilities
        }
        self.state = RuntimeState.IDLE

    @property
    def active_capabilities(self) -> tuple[str, ...]:
        return tuple(self._active)

    @property
    def capability_states(self) -> dict[str, CapabilityState]:
        return dict(self._capability_states)

    def start(self) -> None:
        if self.state is RuntimeState.READY:
            return
        if self.state is RuntimeState.FAILED_DIRTY:
            raise RuntimeIssue(
                StructuredError(
                    code="runtime_dirty",
                    message="runtime cannot restart after an incomplete rollback",
                    action_hint="create a fresh runtime instance",
                )
            )
        self._active.clear()
        for capability_id in self._graph.activation_order:
            provider = self._registry.provider(capability_id)
            context = self._context_for(capability_id)
            self._emit("capability.starting", capability_id=capability_id)
            try:
                provider.prepare(context)
                self._capability_states[capability_id] = CapabilityState.PREPARED
                provider.start(context)
                self._capability_states[capability_id] = CapabilityState.ACTIVE
            except Exception as exc:
                self._capability_states[capability_id] = CapabilityState.FAILED
                primary = StructuredError(
                    code="capability_start_failed",
                    message=f"capability failed during activation: {capability_id}",
                    capability_id=capability_id,
                    cause_category=type(exc).__name__,
                    action_hint="inspect capability diagnostics and configuration",
                    details={"reason": str(exc)},
                )
                self._emit(
                    "capability.failed",
                    capability_id=capability_id,
                    details={"error": primary.to_dict()},
                )
                rollback_errors = self._rollback()
                self.state = (
                    RuntimeState.FAILED_DIRTY if rollback_errors else RuntimeState.FAILED_CLEAN
                )
                self._emit(
                    "runtime.failed",
                    details={
                        "state": self.state.value,
                        "error": primary.to_dict(),
                        "rollback_errors": [error.to_dict() for error in rollback_errors],
                    },
                )
                raise RuntimeActivationError(primary, rollback_errors) from exc
            self._active.append(capability_id)
            self._emit("capability.started", capability_id=capability_id)
        self.state = RuntimeState.READY
        self._emit("runtime.ready", details={"activation_order": self._graph.activation_order})

    def stop(self) -> None:
        if not self._active:
            if self.state is not RuntimeState.FAILED_DIRTY:
                self.state = RuntimeState.STOPPED
            return
        errors = self._stop_active()
        if errors:
            self.state = RuntimeState.FAILED_DIRTY
            primary = StructuredError(
                code="runtime_stop_failed",
                message="one or more capabilities failed during stop",
                details={"count": len(errors)},
            )
            raise RuntimeShutdownError(primary, errors)
        self.state = RuntimeState.STOPPED

    def _context_for(self, capability_id: str) -> BoundRuntimeContext:
        dependency_services: dict[str, object] = {}
        for service_id, provider_id in self._graph.dependencies[capability_id].items():
            provider = self._registry.provider(provider_id)
            dependency_services[service_id] = provider.get_service(service_id)
        return BoundRuntimeContext(
            dependencies=dependency_services,
            configuration=dict(self._configuration.get(capability_id, {})),
            metadata={**self._metadata, "capability_id": capability_id},
            event_sink=self._event_sink,
        )

    def _rollback(self) -> tuple[StructuredError, ...]:
        return self._stop_active()

    def _stop_active(self) -> tuple[StructuredError, ...]:
        errors: list[StructuredError] = []
        for capability_id in reversed(tuple(self._active)):
            provider = self._registry.provider(capability_id)
            context = self._context_for(capability_id)
            self._capability_states[capability_id] = CapabilityState.STOPPING
            self._emit("capability.stopping", capability_id=capability_id)
            try:
                provider.stop(context)
            except Exception as exc:
                self._capability_states[capability_id] = CapabilityState.FAILED
                error = StructuredError(
                    code="capability_stop_failed",
                    message=f"capability failed during stop: {capability_id}",
                    capability_id=capability_id,
                    cause_category=type(exc).__name__,
                    details={"reason": str(exc)},
                )
                errors.append(error)
                self._emit(
                    "capability.failed",
                    capability_id=capability_id,
                    details={"error": error.to_dict()},
                )
            else:
                self._capability_states[capability_id] = CapabilityState.STOPPED
                self._emit("capability.stopped", capability_id=capability_id)
                self._active.remove(capability_id)
        return tuple(errors)

    def _emit(
        self,
        event_type: str,
        *,
        capability_id: str | None = None,
        details: dict[str, Any] | None = None,
    ) -> None:
        self._event_sink.emit(
            RuntimeEvent(type=event_type, capability_id=capability_id, details=details or {})
        )
