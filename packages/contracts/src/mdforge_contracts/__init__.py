from __future__ import annotations

import json
import re
from dataclasses import asdict, dataclass, field
from enum import StrEnum
from typing import Any, Protocol, runtime_checkable

from packaging.specifiers import InvalidSpecifier, SpecifierSet
from packaging.version import InvalidVersion, Version
from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

__version__ = "0.1.0"

_ID_PATTERN = re.compile(r"^[a-z0-9]+(?:[._-][a-z0-9]+)*$")


def _validate_id(value: str) -> str:
    if not _ID_PATTERN.fullmatch(value):
        raise ValueError("identifier must use lowercase alphanumerics separated by '.', '_' or '-'")
    return value


def _validate_version(value: str) -> str:
    try:
        Version(value)
    except InvalidVersion as exc:
        raise ValueError(f"invalid version: {value}") from exc
    return value


class CapabilityKind(StrEnum):
    NATIVE = "native"
    EXECUTABLE = "executable"
    SERVICE = "service"
    MCP = "mcp"
    PLATFORM = "platform"


class _ContractModel(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    def canonical_json(self) -> str:
        return json.dumps(
            self.model_dump(mode="json", exclude_none=True),
            sort_keys=True,
            separators=(",", ":"),
        )


class CapabilityIdentity(_ContractModel):
    id: str
    version: str
    kind: CapabilityKind

    _id_validator = field_validator("id")(_validate_id)
    _version_validator = field_validator("version")(_validate_version)


class ServiceContract(_ContractModel):
    service_id: str
    version: str = "1.0.0"

    _service_validator = field_validator("service_id")(_validate_id)
    _version_validator = field_validator("version")(_validate_version)


class Requirement(_ContractModel):
    service_id: str
    version_specifier: str = ""
    optional: bool = False
    provider_selection: str | None = None

    _service_validator = field_validator("service_id")(_validate_id)

    @field_validator("version_specifier")
    @classmethod
    def validate_specifier(cls, value: str) -> str:
        try:
            SpecifierSet(value)
        except InvalidSpecifier as exc:
            raise ValueError(f"invalid version specifier: {value}") from exc
        return value

    @field_validator("provider_selection")
    @classmethod
    def validate_provider_selection(cls, value: str | None) -> str | None:
        return _validate_id(value) if value is not None else None


class CapabilityManifest(_ContractModel):
    id: str
    version: str
    kind: CapabilityKind
    provides: tuple[ServiceContract, ...] = ()
    requires: tuple[Requirement, ...] = ()
    optional_requires: tuple[Requirement, ...] = ()
    platforms: tuple[str, ...] = ("any",)
    configuration_schema: dict[str, Any] = Field(default_factory=dict)
    entrypoint: str
    lifecycle: str = "managed"
    effects: tuple[str, ...] = ()

    _id_validator = field_validator("id")(_validate_id)
    _version_validator = field_validator("version")(_validate_version)

    @property
    def identity(self) -> CapabilityIdentity:
        return CapabilityIdentity(id=self.id, version=self.version, kind=self.kind)


class RuntimeBundle(_ContractModel):
    id: str
    version: str
    capabilities: tuple[str, ...]
    provider_selections: dict[str, str] = Field(default_factory=dict)
    configuration_overlays: dict[str, dict[str, Any]] = Field(default_factory=dict)

    _id_validator = field_validator("id")(_validate_id)
    _version_validator = field_validator("version")(_validate_version)

    @field_validator("capabilities")
    @classmethod
    def validate_capabilities(cls, values: tuple[str, ...]) -> tuple[str, ...]:
        if len(set(values)) != len(values):
            raise ValueError("bundle capability selections must be unique")
        return tuple(_validate_id(value) for value in values)

    @field_validator("provider_selections")
    @classmethod
    def validate_provider_selections(cls, values: dict[str, str]) -> dict[str, str]:
        return {_validate_id(key): _validate_id(value) for key, value in values.items()}

    @model_validator(mode="after")
    def validate_configuration_overlays(self) -> RuntimeBundle:
        selected = set(self.capabilities)
        unknown = sorted(set(self.configuration_overlays) - selected)
        if unknown:
            raise ValueError(
                "configuration overlays must target selected capabilities: "
                + ", ".join(unknown)
            )
        for capability_id in self.configuration_overlays:
            _validate_id(capability_id)
        return self


@dataclass(frozen=True, slots=True)
class RuntimeEvent:
    type: str
    capability_id: str | None = None
    service_id: str | None = None
    details: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class StructuredError:
    code: str
    message: str
    capability_id: str | None = None
    service_id: str | None = None
    cause_category: str | None = None
    action_hint: str | None = None
    details: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@runtime_checkable
class EventSink(Protocol):
    def emit(self, event: RuntimeEvent) -> None: ...


@runtime_checkable
class RuntimeContext(Protocol):
    configuration: dict[str, Any]
    metadata: dict[str, Any]
    event_sink: EventSink

    def get(self, service_id: str) -> object: ...


@runtime_checkable
class CapabilityProvider(Protocol):
    def manifest(self) -> CapabilityManifest: ...

    def prepare(self, context: RuntimeContext) -> None: ...

    def start(self, context: RuntimeContext) -> None: ...

    def stop(self, context: RuntimeContext) -> None: ...

    def get_service(self, service_id: str) -> object: ...


__all__ = [
    "CapabilityIdentity",
    "CapabilityKind",
    "CapabilityManifest",
    "CapabilityProvider",
    "EventSink",
    "Requirement",
    "RuntimeBundle",
    "RuntimeContext",
    "RuntimeEvent",
    "ServiceContract",
    "StructuredError",
]
