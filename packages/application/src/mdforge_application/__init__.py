from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, cast

from mdforge_contracts import EventSink, RuntimeBundle, StructuredError
from mdforge_kernel import (
    CapabilityRegistry,
    CapabilityRuntime,
    DependencyResolver,
    EventCollector,
    RuntimeActivationError,
    RuntimeState,
    discover_entry_points,
)

__version__ = "0.1.0"


def _json_native(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(key): _json_native(item) for key, item in value.items()}
    if isinstance(value, (tuple, list)):
        return [_json_native(item) for item in value]
    return value


def _json_dict(value: dict[str, Any]) -> dict[str, Any]:
    return cast(dict[str, Any], _json_native(value))


@dataclass(frozen=True, slots=True)
class CapabilityInfo:
    id: str
    version: str
    kind: str
    provides: tuple[str, ...]
    requires: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        return _json_dict(asdict(self))


@dataclass(frozen=True, slots=True)
class DoctorReport:
    ready: bool
    capability_count: int
    discovery_failures: tuple[dict[str, Any], ...]
    runtime: str

    def to_dict(self) -> dict[str, Any]:
        return _json_dict(asdict(self))


@dataclass(frozen=True, slots=True)
class RuntimeReport:
    state: str
    activation_order: tuple[str, ...]
    active_capabilities: tuple[str, ...]
    events: tuple[dict[str, Any], ...]
    error: dict[str, Any] | None = None
    rollback_errors: tuple[dict[str, Any], ...] = ()

    def to_dict(self) -> dict[str, Any]:
        return _json_dict(asdict(self))


class MdforgeApplication:
    def __init__(self) -> None:
        self._runtime: CapabilityRuntime | None = None
        self._events: EventCollector | None = None
        self._activation_order: tuple[str, ...] = ()

    def _registry(
        self, event_sink: EventSink | None = None
    ) -> tuple[CapabilityRegistry, tuple[StructuredError, ...]]:
        discovery = discover_entry_points(event_sink=event_sink)
        registry = CapabilityRegistry()
        failures = list(discovery.failures)
        for provider in discovery.providers:
            try:
                registry.register(provider)
            except Exception as exc:
                error = getattr(exc, "error", None)
                if isinstance(error, StructuredError):
                    failures.append(error)
                else:
                    failures.append(
                        StructuredError(
                            code="capability_registration_failed",
                            message="failed to register discovered capability",
                            cause_category=type(exc).__name__,
                            details={"reason": str(exc)},
                        )
                    )
        return registry, tuple(failures)

    def inspect_capabilities(self) -> tuple[CapabilityInfo, ...]:
        registry, _ = self._registry()
        snapshot = registry.snapshot()
        return tuple(
            CapabilityInfo(
                id=item["id"],
                version=item["version"],
                kind=item["kind"],
                provides=item["provides"],
                requires=item["requires"],
            )
            for item in snapshot.capabilities
        )

    def doctor(self) -> DoctorReport:
        registry, failures = self._registry()
        return DoctorReport(
            ready=not failures,
            capability_count=len(registry.capability_ids()),
            discovery_failures=tuple(error.to_dict() for error in failures),
            runtime="mdforge-t1",
        )

    def resolve_runtime(self, bundle: RuntimeBundle | None = None) -> tuple[str, ...]:
        registry, failures = self._registry()
        if failures:
            raise RuntimeError("capability discovery contains failures")
        return DependencyResolver(registry).resolve(bundle).activation_order

    def start_runtime(self, bundle: RuntimeBundle | None = None) -> RuntimeReport:
        events = EventCollector()
        registry, failures = self._registry(events)
        if failures:
            raise RuntimeError("capability discovery contains failures")
        graph = DependencyResolver(registry).resolve(bundle, event_sink=events)
        runtime = CapabilityRuntime(
            registry,
            graph,
            event_sink=events,
            configuration=bundle.configuration_overlays if bundle is not None else None,
            metadata={"runtime": "mdforge-t1"},
        )
        runtime.start()
        self._runtime = runtime
        self._events = events
        self._activation_order = graph.activation_order
        return self._report()

    def try_start_runtime(self, bundle: RuntimeBundle | None = None) -> RuntimeReport:
        events = EventCollector()
        registry, failures = self._registry(events)
        if failures:
            first = failures[0]
            return RuntimeReport(
                state="failed-clean",
                activation_order=(),
                active_capabilities=(),
                events=tuple(event.to_dict() for event in events.events),
                error=first.to_dict(),
            )
        graph = DependencyResolver(registry).resolve(bundle, event_sink=events)
        runtime = CapabilityRuntime(
            registry,
            graph,
            event_sink=events,
            configuration=bundle.configuration_overlays if bundle is not None else None,
            metadata={"runtime": "mdforge-t1"},
        )
        self._runtime = runtime
        self._events = events
        self._activation_order = graph.activation_order
        try:
            runtime.start()
        except RuntimeActivationError as exc:
            return RuntimeReport(
                state=runtime.state.value,
                activation_order=graph.activation_order,
                active_capabilities=runtime.active_capabilities,
                events=tuple(event.to_dict() for event in events.events),
                error=exc.error.to_dict(),
                rollback_errors=tuple(error.to_dict() for error in exc.rollback_errors),
            )
        return self._report()

    def stop_runtime(self) -> RuntimeReport:
        if self._runtime is None:
            return RuntimeReport(
                state=RuntimeState.STOPPED.value,
                activation_order=(),
                active_capabilities=(),
                events=(),
            )
        self._runtime.stop()
        return self._report()

    def _report(self) -> RuntimeReport:
        assert self._runtime is not None
        assert self._events is not None
        return RuntimeReport(
            state=self._runtime.state.value,
            activation_order=self._activation_order,
            active_capabilities=self._runtime.active_capabilities,
            events=tuple(event.to_dict() for event in self._events.events),
        )


__all__ = [
    "CapabilityInfo",
    "DoctorReport",
    "MdforgeApplication",
    "RuntimeReport",
]
