from __future__ import annotations

from mdforge_application import MdforgeApplication
from mdforge_contracts import RuntimeBundle
from mdforge_kernel import discover_entry_points


def test_reference_capabilities_are_discovered_through_real_entry_points() -> None:
    result = discover_entry_points()
    ids = {provider.manifest().id for provider in result.providers}
    assert {"reference.echo", "reference.consumer", "reference.failing"}.issubset(ids)
    assert result.failures == ()


def test_application_runs_reference_dependency_and_exposes_same_structured_truth() -> None:
    app = MdforgeApplication()
    bundle = RuntimeBundle(
        id="runtime.reference",
        version="1.0.0",
        capabilities=("reference.echo", "reference.consumer"),
        configuration_overlays={"reference.consumer": {"message": "hello"}},
    )
    report = app.start_runtime(bundle)
    assert report.state == "ready"
    assert any(
        event["type"] == "reference.consumer.consumed"
        and event["details"]["result"] == "echo:hello"
        for event in report.events
    )
    stopped = app.stop_runtime()
    assert stopped.state == "stopped"


def test_doctor_and_capabilities_use_structured_application_dtos() -> None:
    app = MdforgeApplication()
    doctor = app.doctor()
    capabilities = app.inspect_capabilities()
    assert doctor.ready is True
    assert doctor.capability_count >= 3
    assert {item.id for item in capabilities}.issuperset({"reference.echo", "reference.consumer"})
    assert doctor.to_dict()["ready"] is True


def test_runtime_events_cover_discovery_validation_resolution_and_lifecycle() -> None:
    app = MdforgeApplication()
    bundle = RuntimeBundle(
        id="runtime.events",
        version="1.0.0",
        capabilities=("reference.echo", "reference.consumer"),
    )
    report = app.start_runtime(bundle)
    event_types = [event["type"] for event in report.events]
    for required in (
        "capability.discovered",
        "capability.validated",
        "capability.resolved",
        "capability.starting",
        "capability.started",
        "runtime.ready",
    ):
        assert required in event_types
    app.stop_runtime()
