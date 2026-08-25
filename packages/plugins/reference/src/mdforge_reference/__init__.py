from __future__ import annotations

from typing import cast

from mdforge_contracts import (
    CapabilityKind,
    CapabilityManifest,
    Requirement,
    RuntimeContext,
    RuntimeEvent,
    ServiceContract,
)


class EchoCapability:
    def manifest(self) -> CapabilityManifest:
        return CapabilityManifest(
            id="reference.echo",
            version="1.0.0",
            kind=CapabilityKind.NATIVE,
            provides=(ServiceContract(service_id="reference.echo", version="1.0.0"),),
            entrypoint="mdforge_reference:echo_plugin",
            lifecycle="managed",
        )

    def prepare(self, context: RuntimeContext) -> None:
        return None

    def start(self, context: RuntimeContext) -> None:
        return None

    def stop(self, context: RuntimeContext) -> None:
        return None

    def get_service(self, service_id: str) -> object:
        if service_id != "reference.echo":
            raise KeyError(service_id)
        return self

    def echo(self, value: str) -> str:
        return f"echo:{value}"


class ConsumerCapability:
    def manifest(self) -> CapabilityManifest:
        return CapabilityManifest(
            id="reference.consumer",
            version="1.0.0",
            kind=CapabilityKind.NATIVE,
            provides=(ServiceContract(service_id="reference.consumer", version="1.0.0"),),
            requires=(Requirement(service_id="reference.echo", version_specifier=">=1,<2"),),
            entrypoint="mdforge_reference:consumer_plugin",
            lifecycle="managed",
        )

    def prepare(self, context: RuntimeContext) -> None:
        return None

    def start(self, context: RuntimeContext) -> None:
        echo = cast(EchoCapability, context.get("reference.echo"))
        message = str(context.configuration.get("message", "hello"))
        context.event_sink.emit(
            RuntimeEvent(
                type="reference.consumer.consumed",
                capability_id="reference.consumer",
                service_id="reference.echo",
                details={"result": echo.echo(message)},
            )
        )

    def stop(self, context: RuntimeContext) -> None:
        return None

    def get_service(self, service_id: str) -> object:
        if service_id != "reference.consumer":
            raise KeyError(service_id)
        return self


class FailingCapability:
    def manifest(self) -> CapabilityManifest:
        return CapabilityManifest(
            id="reference.failing",
            version="1.0.0",
            kind=CapabilityKind.NATIVE,
            provides=(ServiceContract(service_id="reference.failing", version="1.0.0"),),
            requires=(Requirement(service_id="reference.echo"),),
            entrypoint="mdforge_reference:failing_plugin",
            lifecycle="managed",
        )

    def prepare(self, context: RuntimeContext) -> None:
        return None

    def start(self, context: RuntimeContext) -> None:
        raise RuntimeError("intentional reference activation failure")

    def stop(self, context: RuntimeContext) -> None:
        return None

    def get_service(self, service_id: str) -> object:
        if service_id != "reference.failing":
            raise KeyError(service_id)
        return self


def echo_plugin() -> EchoCapability:
    return EchoCapability()


def consumer_plugin() -> ConsumerCapability:
    return ConsumerCapability()


def failing_plugin() -> FailingCapability:
    return FailingCapability()
