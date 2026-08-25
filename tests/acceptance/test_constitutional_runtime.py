from __future__ import annotations

import importlib.util
from pathlib import Path

from mdforge_application import MdforgeApplication
from mdforge_contracts import RuntimeBundle

DOCUMENT_TERMS = (
    "markdown",
    "chapter",
    "section",
    "thesis",
    "citation",
    "docx",
    "word",
    "pdf",
    "wust",
    "renderer",
    "publication",
)


def test_kernel_contains_no_document_domain_vocabulary() -> None:
    spec = importlib.util.find_spec("mdforge_kernel")
    assert spec is not None and spec.origin is not None
    root = Path(spec.origin).parent
    source = "\n".join(path.read_text(encoding="utf-8").lower() for path in root.rglob("*.py"))
    for term in DOCUMENT_TERMS:
        assert term not in source


def test_reference_runtime_constitutional_happy_path_and_clean_failure() -> None:
    app = MdforgeApplication()
    healthy = RuntimeBundle(
        id="runtime.healthy",
        version="1.0.0",
        capabilities=("reference.echo", "reference.consumer"),
    )
    healthy_report = app.start_runtime(healthy)
    assert healthy_report.activation_order == ("reference.echo", "reference.consumer")
    assert healthy_report.state == "ready"
    assert app.stop_runtime().state == "stopped"

    failing = RuntimeBundle(
        id="runtime.failing",
        version="1.0.0",
        capabilities=("reference.echo", "reference.failing"),
    )
    failure = app.try_start_runtime(failing)
    assert failure.state == "failed-clean"
    assert failure.error is not None
    assert failure.error["capability_id"] == "reference.failing"
    assert failure.active_capabilities == ()
