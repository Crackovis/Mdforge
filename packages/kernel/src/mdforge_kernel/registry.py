from __future__ import annotations

from dataclasses import dataclass
from typing import TypedDict

from mdforge_contracts import CapabilityManifest, CapabilityProvider, StructuredError

from .errors import RuntimeIssue


class CapabilitySnapshot(TypedDict):
    id: str
    version: str
    kind: str
    provides: tuple[str, ...]
    requires: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class RegistrySnapshot:
    capabilities: tuple[CapabilitySnapshot, ...]
    services: dict[str, tuple[str, ...]]


class CapabilityRegistry:
    def __init__(self) -> None:
        self._providers: dict[str, CapabilityProvider] = {}
        self._manifests: dict[str, CapabilityManifest] = {}
        self._services: dict[str, list[str]] = {}

    def register(self, provider: CapabilityProvider) -> None:
        manifest = provider.manifest()
        if manifest.id in self._providers:
            raise RuntimeIssue(
                StructuredError(
                    code="duplicate_capability",
                    message=f"duplicate capability id: {manifest.id}",
                    capability_id=manifest.id,
                    action_hint="remove the duplicate or assign a distinct capability id",
                )
            )
        self._providers[manifest.id] = provider
        self._manifests[manifest.id] = manifest
        for service in manifest.provides:
            self._services.setdefault(service.service_id, []).append(manifest.id)
            self._services[service.service_id].sort()

    def provider(self, capability_id: str) -> CapabilityProvider:
        try:
            return self._providers[capability_id]
        except KeyError as exc:
            raise RuntimeIssue(
                StructuredError(
                    code="unknown_capability",
                    message=f"unknown capability: {capability_id}",
                    capability_id=capability_id,
                )
            ) from exc

    def manifest(self, capability_id: str) -> CapabilityManifest:
        try:
            return self._manifests[capability_id]
        except KeyError as exc:
            raise RuntimeIssue(
                StructuredError(
                    code="unknown_capability",
                    message=f"unknown capability: {capability_id}",
                    capability_id=capability_id,
                )
            ) from exc

    def capability_ids(self) -> tuple[str, ...]:
        return tuple(sorted(self._providers))

    def providers_for(self, service_id: str) -> tuple[str, ...]:
        return tuple(self._services.get(service_id, ()))

    def snapshot(self) -> RegistrySnapshot:
        capabilities = tuple(
            CapabilitySnapshot(
                id=manifest.id,
                version=manifest.version,
                kind=manifest.kind.value,
                provides=tuple(service.service_id for service in manifest.provides),
                requires=tuple(requirement.service_id for requirement in manifest.requires),
            )
            for manifest in (self._manifests[key] for key in sorted(self._manifests))
        )
        services = {key: tuple(self._services[key]) for key in sorted(self._services)}
        return RegistrySnapshot(capabilities=capabilities, services=services)
