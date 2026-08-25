from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from mdforge_contracts import EventSink, RuntimeEvent


@dataclass(slots=True)
class EventCollector(EventSink):
    events: list[RuntimeEvent] = field(default_factory=list)

    def emit(self, event: RuntimeEvent) -> None:
        self.events.append(event)


@dataclass(slots=True)
class BoundRuntimeContext:
    dependencies: dict[str, object]
    configuration: dict[str, Any]
    metadata: dict[str, Any]
    event_sink: EventSink

    def get(self, service_id: str) -> object:
        if service_id not in self.dependencies:
            raise KeyError(service_id)
        return self.dependencies[service_id]
