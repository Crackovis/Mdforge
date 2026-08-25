from __future__ import annotations

import pytest
from mdforge_contracts import (
    CapabilityIdentity,
    CapabilityKind,
    CapabilityManifest,
    Requirement,
    RuntimeBundle,
    RuntimeEvent,
    ServiceContract,
    StructuredError,
)
from pydantic import ValidationError


def test_capability_manifest_is_validated_and_serialized_deterministically() -> None:
    manifest = CapabilityManifest(
        id="reference.consumer",
        version="1.2.0",
        kind=CapabilityKind.NATIVE,
        provides=(ServiceContract(service_id="reference.consumer", version="1.2.0"),),
        requires=(Requirement(service_id="reference.echo", version_specifier=">=1,<2"),),
        optional_requires=(),
        platforms=("any",),
        configuration_schema={"type": "object"},
        entrypoint="reference.consumer:plugin",
        lifecycle="managed",
        effects=("memory",),
    )
    assert manifest.identity == CapabilityIdentity(
        id="reference.consumer", version="1.2.0", kind=CapabilityKind.NATIVE
    )
    assert manifest.canonical_json() == manifest.canonical_json()
    assert '"reference.consumer"' in manifest.canonical_json()


@pytest.mark.parametrize(("field", "value"), [("id", "Invalid ID"), ("version", "not-a-version")])
def test_capability_identity_rejects_invalid_values(field: str, value: str) -> None:
    payload = {"id": "reference.echo", "version": "1.0.0", "kind": "native"}
    payload[field] = value
    with pytest.raises(ValidationError):
        CapabilityIdentity.model_validate(payload)


def test_requirement_rejects_invalid_version_specifier() -> None:
    with pytest.raises(ValidationError):
        Requirement(service_id="reference.echo", version_specifier="=>1")


def test_bundle_is_generic_and_deterministic() -> None:
    bundle = RuntimeBundle(
        id="runtime.reference",
        version="1.0.0",
        capabilities=("reference.consumer", "reference.echo"),
        provider_selections={"reference.echo": "reference.echo"},
        configuration_overlays={"reference.consumer": {"message": "hello"}},
    )
    assert bundle.capabilities == ("reference.consumer", "reference.echo")
    assert "thesis" not in bundle.canonical_json().lower()
    assert bundle.canonical_json() == bundle.canonical_json()


def test_events_and_errors_are_structured() -> None:
    event = RuntimeEvent(type="capability.started", capability_id="reference.echo")
    issue = StructuredError(
        code="capability_start_failed",
        message="start failed",
        capability_id="reference.echo",
        cause_category="runtime",
        action_hint="inspect capability diagnostics",
    )
    assert event.to_dict()["type"] == "capability.started"
    assert issue.to_dict()["code"] == "capability_start_failed"


def test_capability_manifest_rejects_incomplete_payload() -> None:
    with pytest.raises(ValidationError):
        CapabilityManifest.model_validate({"id": "incomplete", "version": "1.0.0"})


def test_bundle_rejects_configuration_overlay_for_unselected_capability() -> None:
    with pytest.raises(ValidationError):
        RuntimeBundle(
            id="runtime.bounded",
            version="1.0.0",
            capabilities=("reference.echo",),
            configuration_overlays={"reference.consumer": {"message": "nope"}},
        )
