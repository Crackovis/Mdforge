from __future__ import annotations

from dataclasses import dataclass

from mdforge_contracts import EventSink, Requirement, RuntimeBundle, RuntimeEvent, StructuredError
from packaging.specifiers import SpecifierSet
from packaging.version import Version

from .errors import RuntimeIssue
from .registry import CapabilityRegistry


@dataclass(frozen=True, slots=True)
class ResolvedGraph:
    activation_order: tuple[str, ...]
    dependencies: dict[str, dict[str, str]]
    selected_capabilities: tuple[str, ...]


class DependencyResolver:
    def __init__(self, registry: CapabilityRegistry) -> None:
        self._registry = registry

    def resolve(
        self,
        bundle: RuntimeBundle | None = None,
        *,
        event_sink: EventSink | None = None,
    ) -> ResolvedGraph:
        selected = self._selected_ids(bundle)
        selected_set = set(selected)
        dependencies: dict[str, dict[str, str]] = {capability_id: {} for capability_id in selected}

        for capability_id in selected:
            manifest = self._registry.manifest(capability_id)
            requirements = tuple(manifest.requires) + tuple(
                req.model_copy(update={"optional": True}) for req in manifest.optional_requires
            )
            for requirement in requirements:
                provider_id = self._resolve_requirement(
                    capability_id,
                    requirement,
                    selected_set,
                    bundle,
                )
                if provider_id is not None:
                    dependencies[capability_id][requirement.service_id] = provider_id

        activation_order = self._stable_topological_order(dependencies)
        if event_sink is not None:
            for capability_id in activation_order:
                event_sink.emit(
                    RuntimeEvent(
                        type="capability.resolved",
                        capability_id=capability_id,
                        details={"dependencies": dict(dependencies[capability_id])},
                    )
                )
        return ResolvedGraph(
            activation_order=activation_order,
            dependencies=dependencies,
            selected_capabilities=selected,
        )

    def _selected_ids(self, bundle: RuntimeBundle | None) -> tuple[str, ...]:
        if bundle is None:
            return self._registry.capability_ids()
        selected = tuple(sorted(bundle.capabilities))
        for capability_id in selected:
            self._registry.manifest(capability_id)
        return selected

    def _resolve_requirement(
        self,
        consumer_id: str,
        requirement: Requirement,
        selected: set[str],
        bundle: RuntimeBundle | None,
    ) -> str | None:
        candidates = [
            provider_id
            for provider_id in self._registry.providers_for(requirement.service_id)
            if provider_id in selected
            and self._service_version_matches(provider_id, requirement)
        ]

        requested_provider = requirement.provider_selection
        if bundle is not None:
            requested_provider = bundle.provider_selections.get(
                requirement.service_id, requested_provider
            )
        if requested_provider is not None:
            if requested_provider not in candidates:
                raise RuntimeIssue(
                    StructuredError(
                        code="provider_selection_invalid",
                        message=(
                            f"selected provider {requested_provider} cannot satisfy "
                            f"{requirement.service_id} for {consumer_id}"
                        ),
                        capability_id=consumer_id,
                        service_id=requirement.service_id,
                        details={"provider": requested_provider},
                    )
                )
            return requested_provider

        if not candidates:
            if requirement.optional:
                return None
            available = [
                provider_id
                for provider_id in self._registry.providers_for(requirement.service_id)
                if provider_id in selected
            ]
            code = "incompatible_provider" if available else "missing_provider"
            raise RuntimeIssue(
                StructuredError(
                    code=code,
                    message=f"no compatible provider for {requirement.service_id}",
                    capability_id=consumer_id,
                    service_id=requirement.service_id,
                    details={"available": available, "specifier": requirement.version_specifier},
                    action_hint="install or select a compatible provider",
                )
            )
        if len(candidates) > 1:
            raise RuntimeIssue(
                StructuredError(
                    code="ambiguous_provider",
                    message=f"multiple providers for {requirement.service_id}",
                    capability_id=consumer_id,
                    service_id=requirement.service_id,
                    details={"providers": sorted(candidates)},
                    action_hint="select a provider explicitly in the runtime bundle",
                )
            )
        return candidates[0]

    def _service_version_matches(self, provider_id: str, requirement: Requirement) -> bool:
        manifest = self._registry.manifest(provider_id)
        specifier = SpecifierSet(requirement.version_specifier)
        for service in manifest.provides:
            if service.service_id == requirement.service_id:
                return not requirement.version_specifier or Version(service.version) in specifier
        return False

    def _stable_topological_order(
        self, dependencies: dict[str, dict[str, str]]
    ) -> tuple[str, ...]:
        predecessors = {
            capability_id: set(provider_map.values())
            for capability_id, provider_map in dependencies.items()
        }
        order: list[str] = []
        remaining = {key: set(value) for key, value in predecessors.items()}
        while remaining:
            ready = sorted(key for key, value in remaining.items() if not value)
            if not ready:
                cycle = self._find_cycle(predecessors)
                raise RuntimeIssue(
                    StructuredError(
                        code="dependency_cycle",
                        message="dependency cycle detected",
                        details={"cycle": cycle},
                        action_hint="remove one dependency edge in the reported cycle",
                    )
                )
            for capability_id in ready:
                order.append(capability_id)
                remaining.pop(capability_id)
            ready_set = set(ready)
            for value in remaining.values():
                value.difference_update(ready_set)
        return tuple(order)

    @staticmethod
    def _find_cycle(predecessors: dict[str, set[str]]) -> tuple[str, ...]:
        visiting: set[str] = set()
        visited: set[str] = set()
        stack: list[str] = []

        def visit(node: str) -> tuple[str, ...] | None:
            if node in visiting:
                start = stack.index(node)
                return tuple([*stack[start:], node])
            if node in visited:
                return None
            visiting.add(node)
            stack.append(node)
            for dependency in sorted(predecessors.get(node, ())):
                cycle = visit(dependency)
                if cycle is not None:
                    return cycle
            stack.pop()
            visiting.remove(node)
            visited.add(node)
            return None

        for node in sorted(predecessors):
            cycle = visit(node)
            if cycle is not None:
                return cycle
        return ()
