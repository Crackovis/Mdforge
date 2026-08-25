from __future__ import annotations

from importlib.metadata import EntryPoint

from mdforge_kernel import discover_embedded, discover_entry_points
from mdforge_reference import EchoCapability


def test_broken_entry_point_does_not_hide_healthy_provider() -> None:
    healthy = EntryPoint(
        name="healthy",
        value="mdforge_reference:echo_plugin",
        group="mdforge.capabilities",
    )
    broken = EntryPoint(
        name="broken",
        value="module_that_does_not_exist:plugin",
        group="mdforge.capabilities",
    )
    result = discover_entry_points(entries=(broken, healthy))
    assert [provider.manifest().id for provider in result.providers] == ["reference.echo"]
    assert len(result.failures) == 1
    assert result.failures[0].code == "capability_discovery_failed"


def test_embedded_provider_discovery_validates_without_entry_points() -> None:
    result = discover_embedded((EchoCapability(),))
    assert [provider.manifest().id for provider in result.providers] == ["reference.echo"]
    assert result.failures == ()
