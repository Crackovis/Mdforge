from __future__ import annotations

from typing import Any

import pytest
from mdforge_contracts import (
    CapabilityKind,
    CapabilityManifest,
    Requirement,
    RuntimeBundle,
    ServiceContract,
)
from mdforge_kernel import CapabilityRegistry, DependencyResolver, RuntimeIssue


class Provider:
    def __init__(
        self,
        capability_id: str,
        *,
        provides: tuple[tuple[str, str], ...],
        requires: tuple[Requirement, ...] = (),
    ) -> None:
        self._manifest = CapabilityManifest(
            id=capability_id,
            version="1.0.0",
            kind=CapabilityKind.NATIVE,
            provides=tuple(ServiceContract(service_id=s, version=v) for s, v in provides),
            requires=requires,
            entrypoint=f"tests:{capability_id}",
            lifecycle="managed",
        )

    def manifest(self) -> CapabilityManifest:
        return self._manifest

    def prepare(self, context: Any) -> None:
        return None

    def start(self, context: Any) -> None:
        return None

    def stop(self, context: Any) -> None:
        return None

    def get_service(self, service_id: str) -> object:
        return self


def make_registry(*providers: Provider) -> CapabilityRegistry:
    registry = CapabilityRegistry()
    for provider in providers:
        registry.register(provider)
    return registry


def test_registry_indexes_capabilities_and_services_deterministically() -> None:
    registry = make_registry(
        Provider("provider.b", provides=(("service.b", "1.0.0"),)),
        Provider("provider.a", provides=(("service.a", "1.0.0"),)),
    )
    snapshot = registry.snapshot()
    assert [item["id"] for item in snapshot.capabilities] == ["provider.a", "provider.b"]
    assert snapshot.services == {"service.a": ("provider.a",), "service.b": ("provider.b",)}


def test_registry_rejects_duplicate_capability_id() -> None:
    registry = make_registry(Provider("provider.a", provides=(("service.a", "1.0.0"),)))
    with pytest.raises(RuntimeIssue, match="duplicate") as raised:
        registry.register(Provider("provider.a", provides=(("service.other", "1.0.0"),)))
    assert raised.value.error.code == "duplicate_capability"


def test_dependency_resolution_is_stable_and_provider_first() -> None:
    echo = Provider("reference.echo", provides=(("reference.echo", "1.2.0"),))
    consumer = Provider(
        "reference.consumer",
        provides=(("reference.consumer", "1.0.0"),),
        requires=(Requirement(service_id="reference.echo", version_specifier=">=1,<2"),),
    )
    graph = DependencyResolver(make_registry(consumer, echo)).resolve()
    assert graph.activation_order == ("reference.echo", "reference.consumer")
    assert graph.dependencies["reference.consumer"] == {"reference.echo": "reference.echo"}


def test_missing_provider_is_a_structured_error() -> None:
    consumer = Provider(
        "consumer",
        provides=(("consumer", "1.0.0"),),
        requires=(Requirement(service_id="missing.service"),),
    )
    with pytest.raises(RuntimeIssue) as raised:
        DependencyResolver(make_registry(consumer)).resolve()
    assert raised.value.error.code == "missing_provider"
    assert raised.value.error.service_id == "missing.service"


def test_cycle_is_rejected_with_cycle_path() -> None:
    a = Provider(
        "a",
        provides=(("service.a", "1.0.0"),),
        requires=(Requirement(service_id="service.b"),),
    )
    b = Provider(
        "b",
        provides=(("service.b", "1.0.0"),),
        requires=(Requirement(service_id="service.a"),),
    )
    with pytest.raises(RuntimeIssue) as raised:
        DependencyResolver(make_registry(a, b)).resolve()
    assert raised.value.error.code == "dependency_cycle"
    assert raised.value.error.details["cycle"]


def test_ambiguous_provider_requires_explicit_selection() -> None:
    a = Provider("provider.a", provides=(("service.shared", "1.0.0"),))
    b = Provider("provider.b", provides=(("service.shared", "1.0.0"),))
    consumer = Provider(
        "consumer",
        provides=(("consumer", "1.0.0"),),
        requires=(Requirement(service_id="service.shared"),),
    )
    registry = make_registry(a, b, consumer)
    with pytest.raises(RuntimeIssue) as raised:
        DependencyResolver(registry).resolve()
    assert raised.value.error.code == "ambiguous_provider"
    bundle = RuntimeBundle(
        id="runtime.explicit",
        version="1.0.0",
        capabilities=("consumer", "provider.a", "provider.b"),
        provider_selections={"service.shared": "provider.a"},
    )
    graph = DependencyResolver(registry).resolve(bundle)
    assert graph.dependencies["consumer"] == {"service.shared": "provider.a"}


def test_bundle_with_unknown_capability_is_rejected_explicitly() -> None:
    registry = make_registry(Provider("known", provides=(("service.known", "1.0.0"),)))
    bundle = RuntimeBundle(
        id="runtime.unknown",
        version="1.0.0",
        capabilities=("known", "missing"),
    )
    with pytest.raises(RuntimeIssue) as raised:
        DependencyResolver(registry).resolve(bundle)
    assert raised.value.error.code == "unknown_capability"
    assert raised.value.error.capability_id == "missing"


def test_invalid_explicit_provider_selection_is_rejected() -> None:
    provider = Provider("provider.a", provides=(("service.shared", "1.0.0"),))
    consumer = Provider(
        "consumer",
        provides=(("consumer", "1.0.0"),),
        requires=(Requirement(service_id="service.shared"),),
    )
    bundle = RuntimeBundle(
        id="runtime.invalid-selection",
        version="1.0.0",
        capabilities=("provider.a", "consumer"),
        provider_selections={"service.shared": "provider.missing"},
    )
    with pytest.raises(RuntimeIssue) as raised:
        DependencyResolver(make_registry(provider, consumer)).resolve(bundle)
    assert raised.value.error.code == "provider_selection_invalid"
