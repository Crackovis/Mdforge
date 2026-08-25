from __future__ import annotations

from typing import Any

from mdforge_contracts import CapabilityKind, CapabilityManifest, ServiceContract


class ExternalSample:
    def manifest(self) -> CapabilityManifest:
        return CapabilityManifest(
            id="external.sample",
            version="1.0.0",
            kind=CapabilityKind.NATIVE,
            provides=(ServiceContract(service_id="external.sample", version="1.0.0"),),
            entrypoint="mdforge_external_sample:plugin",
            lifecycle="managed",
        )

    def prepare(self, context: Any) -> None:
        return None

    def start(self, context: Any) -> None:
        return None

    def stop(self, context: Any) -> None:
        return None

    def get_service(self, service_id: str) -> object:
        if service_id != "external.sample":
            raise KeyError(service_id)
        return self


def plugin() -> ExternalSample:
    return ExternalSample()
