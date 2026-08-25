from __future__ import annotations

from typing import Any

import pytest
from mdforge_contracts import CapabilityKind, CapabilityManifest, Requirement, ServiceContract
from mdforge_kernel import (
    CapabilityRegistry,
    CapabilityRuntime,
    DependencyResolver,
    RuntimeActivationError,
    RuntimeIssue,
    RuntimeShutdownError,
    RuntimeState,
)


class EdgeProvider:
    def __init__(
        self,
        capability_id: str,
        service_id: str,
        *,
        service_version: str = "1.0.0",
        requires: tuple[Requirement, ...] = (),
        optional_requires: tuple[Requirement, ...] = (),
        fail_prepare: bool = False,
        fail_start: bool = False,
        fail_stop: bool = False,
    ) -> None:
        self.id = capability_id
        self.service_id = service_id
        self.fail_prepare = fail_prepare
        self.fail_start = fail_start
        self.fail_stop = fail_stop
        self._manifest = CapabilityManifest(
            id=capability_id,
            version="1.0.0",
            kind=CapabilityKind.NATIVE,
            provides=(ServiceContract(service_id=service_id, version=service_version),),
            requires=requires,
            optional_requires=optional_requires,
            entrypoint=f"tests:{capability_id}",
            lifecycle="managed",
        )

    def manifest(self) -> CapabilityManifest:
        return self._manifest

    def prepare(self, context: Any) -> None:
        if self.fail_prepare:
            raise RuntimeError("prepare failed")

    def start(self, context: Any) -> None:
        if self.fail_start:
            raise RuntimeError("start failed")

    def stop(self, context: Any) -> None:
        if self.fail_stop:
            raise RuntimeError("stop failed")

    def get_service(self, service_id: str) -> object:
        if service_id != self.service_id:
            raise KeyError(service_id)
        return self


def registry(*providers: EdgeProvider) -> CapabilityRegistry:
    result = CapabilityRegistry()
    for provider in providers:
        result.register(provider)
    return result


def test_optional_requirement_can_be_absent() -> None:
    provider = EdgeProvider(
        "consumer",
        "consumer",
        optional_requires=(Requirement(service_id="optional.missing"),),
    )
    graph = DependencyResolver(registry(provider)).resolve()
    assert graph.dependencies["consumer"] == {}


def test_incompatible_service_version_is_structured() -> None:
    old = EdgeProvider("old", "service.shared", service_version="1.0.0")
    consumer = EdgeProvider(
        "consumer",
        "consumer",
        requires=(Requirement(service_id="service.shared", version_specifier=">=2"),),
    )
    with pytest.raises(RuntimeIssue) as raised:
        DependencyResolver(registry(old, consumer)).resolve()
    assert raised.value.error.code == "incompatible_provider"
    assert raised.value.error.details["available"] == ["old"]


def test_prepare_failure_rolls_back_prior_capability() -> None:
    a = EdgeProvider("a", "service.a")
    b = EdgeProvider(
        "b",
        "service.b",
        requires=(Requirement(service_id="service.a"),),
        fail_prepare=True,
    )
    reg = registry(a, b)
    runtime = CapabilityRuntime(reg, DependencyResolver(reg).resolve())
    with pytest.raises(RuntimeActivationError):
        runtime.start()
    assert runtime.state is RuntimeState.FAILED_CLEAN
    assert runtime.active_capabilities == ()


def test_clean_failure_can_restart_after_provider_is_repaired() -> None:
    provider = EdgeProvider("unstable", "service.unstable", fail_start=True)
    reg = registry(provider)
    runtime = CapabilityRuntime(reg, DependencyResolver(reg).resolve())
    with pytest.raises(RuntimeActivationError):
        runtime.start()
    assert runtime.state is RuntimeState.FAILED_CLEAN
    provider.fail_start = False
    runtime.start()
    assert runtime.state is RuntimeState.READY
    runtime.stop()
    assert runtime.state is RuntimeState.STOPPED


def test_stop_failure_is_classified_dirty_and_keeps_failed_capability_active() -> None:
    provider = EdgeProvider("sticky", "service.sticky", fail_stop=True)
    reg = registry(provider)
    runtime = CapabilityRuntime(reg, DependencyResolver(reg).resolve())
    runtime.start()
    with pytest.raises(RuntimeShutdownError) as raised:
        runtime.stop()
    assert runtime.state is RuntimeState.FAILED_DIRTY
    assert raised.value.stop_errors[0].capability_id == "sticky"
    assert runtime.active_capabilities == ("sticky",)
