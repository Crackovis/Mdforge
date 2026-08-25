from __future__ import annotations

from typing import Any

import pytest
from mdforge_contracts import CapabilityKind, CapabilityManifest, Requirement, ServiceContract
from mdforge_kernel import (
    BoundRuntimeContext,
    CapabilityRegistry,
    CapabilityRuntime,
    DependencyResolver,
    EventCollector,
    RuntimeActivationError,
    RuntimeState,
)


class LifecycleProvider:
    def __init__(
        self,
        capability_id: str,
        log: list[str],
        *,
        service_id: str,
        requires: tuple[Requirement, ...] = (),
        fail_start: bool = False,
        fail_stop: bool = False,
    ) -> None:
        self.capability_id = capability_id
        self.service_id = service_id
        self.log = log
        self.fail_start = fail_start
        self.fail_stop = fail_stop
        self._manifest = CapabilityManifest(
            id=capability_id,
            version="1.0.0",
            kind=CapabilityKind.NATIVE,
            provides=(ServiceContract(service_id=service_id, version="1.0.0"),),
            requires=requires,
            entrypoint=f"tests:{capability_id}",
            lifecycle="managed",
        )

    def manifest(self) -> CapabilityManifest:
        return self._manifest

    def prepare(self, context: Any) -> None:
        self.log.append(f"prepare:{self.capability_id}")

    def start(self, context: Any) -> None:
        self.log.append(f"start:{self.capability_id}")
        if self.fail_start:
            raise RuntimeError(f"boom:{self.capability_id}")

    def stop(self, context: Any) -> None:
        self.log.append(f"stop:{self.capability_id}")
        if self.fail_stop:
            raise RuntimeError(f"stop-boom:{self.capability_id}")

    def get_service(self, service_id: str) -> object:
        if service_id != self.service_id:
            raise KeyError(service_id)
        return self


def test_bound_context_denies_undeclared_service_lookup() -> None:
    context = BoundRuntimeContext(
        dependencies={"allowed.service": object()},
        configuration={},
        metadata={"runtime_id": "test"},
        event_sink=EventCollector(),
    )
    assert context.get("allowed.service") is not None
    with pytest.raises(KeyError):
        context.get("not.declared")


def test_failed_activation_rolls_back_in_reverse_and_preserves_primary_error() -> None:
    log: list[str] = []
    a = LifecycleProvider("a", log, service_id="service.a")
    b = LifecycleProvider(
        "b", log, service_id="service.b", requires=(Requirement(service_id="service.a"),)
    )
    c = LifecycleProvider(
        "c",
        log,
        service_id="service.c",
        requires=(Requirement(service_id="service.b"),),
        fail_start=True,
    )
    registry = CapabilityRegistry()
    for provider in (a, b, c):
        registry.register(provider)
    graph = DependencyResolver(registry).resolve()
    events = EventCollector()
    runtime = CapabilityRuntime(registry, graph, event_sink=events)

    with pytest.raises(RuntimeActivationError) as raised:
        runtime.start()

    assert raised.value.error.capability_id == "c"
    assert runtime.state is RuntimeState.FAILED_CLEAN
    assert runtime.active_capabilities == ()
    assert log[-2:] == ["stop:b", "stop:a"]
    assert any(event.type == "runtime.failed" for event in events.events)


def test_rollback_failure_is_reported_as_failed_dirty_without_masking_primary_error() -> None:
    log: list[str] = []
    a = LifecycleProvider("a", log, service_id="service.a", fail_stop=True)
    b = LifecycleProvider(
        "b",
        log,
        service_id="service.b",
        requires=(Requirement(service_id="service.a"),),
        fail_start=True,
    )
    registry = CapabilityRegistry()
    for provider in (a, b):
        registry.register(provider)
    runtime = CapabilityRuntime(registry, DependencyResolver(registry).resolve())

    with pytest.raises(RuntimeActivationError) as raised:
        runtime.start()

    assert raised.value.error.capability_id == "b"
    assert runtime.state is RuntimeState.FAILED_DIRTY
    assert raised.value.rollback_errors


def test_healthy_runtime_stops_in_reverse_order() -> None:
    log: list[str] = []
    a = LifecycleProvider("a", log, service_id="service.a")
    b = LifecycleProvider(
        "b", log, service_id="service.b", requires=(Requirement(service_id="service.a"),)
    )
    registry = CapabilityRegistry()
    for provider in (a, b):
        registry.register(provider)
    runtime = CapabilityRuntime(registry, DependencyResolver(registry).resolve())
    runtime.start()
    assert runtime.state is RuntimeState.READY
    runtime.stop()
    assert runtime.state is RuntimeState.STOPPED
    assert log[-2:] == ["stop:b", "stop:a"]


def test_start_and_stop_are_idempotent_in_terminal_runtime_states() -> None:
    log: list[str] = []
    provider = LifecycleProvider("a", log, service_id="service.a")
    registry = CapabilityRegistry()
    registry.register(provider)
    runtime = CapabilityRuntime(registry, DependencyResolver(registry).resolve())

    runtime.start()
    runtime.start()
    assert log.count("prepare:a") == 1
    assert log.count("start:a") == 1

    runtime.stop()
    runtime.stop()
    assert log.count("stop:a") == 1
    assert runtime.state is RuntimeState.STOPPED


def test_runtime_exposes_capability_state_machine() -> None:
    log: list[str] = []
    provider = LifecycleProvider("a", log, service_id="service.a")
    registry = CapabilityRegistry()
    registry.register(provider)
    runtime = CapabilityRuntime(registry, DependencyResolver(registry).resolve())

    assert runtime.capability_states["a"].value == "resolved"
    runtime.start()
    assert runtime.capability_states["a"].value == "active"
    runtime.stop()
    assert runtime.capability_states["a"].value == "stopped"
