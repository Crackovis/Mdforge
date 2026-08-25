from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from importlib.metadata import EntryPoint, entry_points
from typing import Any, cast

from mdforge_contracts import (
    CapabilityManifest,
    CapabilityProvider,
    EventSink,
    RuntimeContext,
    RuntimeEvent,
    StructuredError,
)


@dataclass(frozen=True, slots=True)
class DiscoveryResult:
    providers: tuple[CapabilityProvider, ...]
    failures: tuple[StructuredError, ...]


class _NormalizedProvider:
    def __init__(self, provider: Any, manifest: CapabilityManifest) -> None:
        self._provider = provider
        self._manifest = manifest

    def manifest(self) -> CapabilityManifest:
        return self._manifest

    def prepare(self, context: RuntimeContext) -> None:
        self._provider.prepare(context)

    def start(self, context: RuntimeContext) -> None:
        self._provider.start(context)

    def stop(self, context: RuntimeContext) -> None:
        self._provider.stop(context)

    def get_service(self, service_id: str) -> object:
        return cast(object, self._provider.get_service(service_id))


def _emit(
    event_sink: EventSink | None,
    event_type: str,
    *,
    capability_id: str | None = None,
    details: dict[str, Any] | None = None,
) -> None:
    if event_sink is not None:
        event_sink.emit(
            RuntimeEvent(type=event_type, capability_id=capability_id, details=details or {})
        )


def _normalize_candidate(
    candidate: Any,
    *,
    source: str,
    event_sink: EventSink | None,
) -> CapabilityProvider:
    raw_manifest = candidate.manifest()
    if isinstance(raw_manifest, CapabilityManifest):
        capability_id = raw_manifest.id
    elif isinstance(raw_manifest, dict) and raw_manifest.get("id") is not None:
        capability_id = str(raw_manifest["id"])
    else:
        capability_id = None

    _emit(
        event_sink,
        "capability.discovered",
        capability_id=capability_id,
        details={"source": source},
    )
    manifest = (
        raw_manifest
        if isinstance(raw_manifest, CapabilityManifest)
        else CapabilityManifest.model_validate(raw_manifest)
    )
    if not isinstance(candidate, CapabilityProvider):
        raise TypeError("discovered object does not implement CapabilityProvider")
    provider: CapabilityProvider = (
        candidate
        if isinstance(raw_manifest, CapabilityManifest)
        else _NormalizedProvider(candidate, manifest)
    )
    _emit(
        event_sink,
        "capability.validated",
        capability_id=manifest.id,
        details={"source": source, "version": manifest.version},
    )
    return provider


def _failure(*, name: str, source: str, exc: Exception) -> StructuredError:
    return StructuredError(
        code="capability_discovery_failed",
        message=f"failed to load capability: {name}",
        cause_category=type(exc).__name__,
        details={"source": source, "reason": str(exc)},
        action_hint="inspect or reinstall the failing capability package",
    )


def discover_entry_points(
    *,
    group: str = "mdforge.capabilities",
    entries: Iterable[EntryPoint] | None = None,
    event_sink: EventSink | None = None,
) -> DiscoveryResult:
    selected = list(entries if entries is not None else entry_points(group=group))
    selected.sort(key=lambda item: (item.name, item.value))
    providers: list[CapabilityProvider] = []
    failures: list[StructuredError] = []
    for item in selected:
        try:
            loaded = item.load()
            candidate = loaded() if callable(loaded) else loaded
            providers.append(
                _normalize_candidate(candidate, source=item.value, event_sink=event_sink)
            )
        except Exception as exc:
            failures.append(_failure(name=item.name, source=item.value, exc=exc))
    providers.sort(key=lambda provider: provider.manifest().id)
    return DiscoveryResult(providers=tuple(providers), failures=tuple(failures))


def discover_embedded(
    providers: Iterable[CapabilityProvider],
    *,
    event_sink: EventSink | None = None,
) -> DiscoveryResult:
    discovered: list[CapabilityProvider] = []
    failures: list[StructuredError] = []
    for index, candidate in enumerate(providers):
        source = f"embedded[{index}]"
        try:
            discovered.append(
                _normalize_candidate(candidate, source=source, event_sink=event_sink)
            )
        except Exception as exc:
            failures.append(_failure(name=source, source=source, exc=exc))
    discovered.sort(key=lambda provider: provider.manifest().id)
    return DiscoveryResult(providers=tuple(discovered), failures=tuple(failures))
