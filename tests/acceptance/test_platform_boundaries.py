from __future__ import annotations

import ast
import tomllib
from pathlib import Path

FORBIDDEN_RUNTIME_IMPORTS = {
    "comtypes",
    "fastapi",
    "mcp",
    "pythoncom",
    "socket",
    "sqlite3",
    "subprocess",
    "win32com",
}

PRODUCTION_ROOTS = (
    Path("packages/contracts/src"),
    Path("packages/kernel/src"),
    Path("packages/application/src"),
    Path("packages/cli/src"),
    Path("packages/plugins/reference/src"),
)


def imported_roots(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    roots: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            roots.update(alias.name.split(".", 1)[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            roots.add(node.module.split(".", 1)[0])
    return roots


def test_t1_runtime_has_no_platform_or_deferred_runtime_dependency() -> None:
    imports: dict[str, set[str]] = {}
    for root in PRODUCTION_ROOTS:
        for path in root.rglob("*.py"):
            imports[str(path)] = imported_roots(path)
    offenders = {
        path: sorted(modules & FORBIDDEN_RUNTIME_IMPORTS)
        for path, modules in imports.items()
        if modules & FORBIDDEN_RUNTIME_IMPORTS
    }
    assert offenders == {}


def test_kernel_does_not_depend_on_pluggy() -> None:
    data = tomllib.loads(Path("packages/kernel/pyproject.toml").read_text(encoding="utf-8"))
    dependencies = data["project"].get("dependencies", [])
    assert all(not dependency.lower().startswith("pluggy") for dependency in dependencies)


def test_constitutional_package_import_boundaries() -> None:
    contract_imports: set[str] = set()
    for path in Path("packages/contracts/src").rglob("*.py"):
        contract_imports.update(imported_roots(path))
    assert not contract_imports & {
        "mdforge_application",
        "mdforge_cli",
        "mdforge_kernel",
        "mdforge_reference",
    }

    kernel_imports: set[str] = set()
    for path in Path("packages/kernel/src").rglob("*.py"):
        kernel_imports.update(imported_roots(path))
    assert not kernel_imports & {"mdforge_application", "mdforge_cli", "mdforge_reference"}

    reference_imports: set[str] = set()
    for path in Path("packages/plugins/reference/src").rglob("*.py"):
        reference_imports.update(imported_roots(path))
    assert "mdforge_kernel" not in reference_imports
