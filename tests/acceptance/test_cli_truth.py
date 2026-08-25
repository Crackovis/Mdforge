from __future__ import annotations

import json

from mdforge_application import MdforgeApplication
from mdforge_cli import app
from typer.testing import CliRunner

runner = CliRunner()


def test_doctor_human_and_json_are_backed_by_application_truth() -> None:
    expected = MdforgeApplication().doctor().to_dict()
    json_result = runner.invoke(app, ["doctor", "--json"])
    human_result = runner.invoke(app, ["doctor"])
    assert json_result.exit_code == 0
    assert json.loads(json_result.stdout) == expected
    assert human_result.exit_code == 0
    assert ("READY" if expected["ready"] else "DEGRADED") in human_result.stdout


def test_capabilities_human_and_json_are_backed_by_application_truth() -> None:
    expected = [item.to_dict() for item in MdforgeApplication().inspect_capabilities()]
    json_result = runner.invoke(app, ["capabilities", "--json"])
    human_result = runner.invoke(app, ["capabilities"])
    assert json_result.exit_code == 0
    assert json.loads(json_result.stdout) == expected
    assert human_result.exit_code == 0
    for item in expected:
        assert item["id"] in human_result.stdout
