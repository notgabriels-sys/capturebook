"""Command-line behavior for declared Capturebook preparation packets."""

from __future__ import annotations

from capturebook.cli import main
from tests.helpers import write_plan


def test_check_reports_explicit_capture_boundary_without_writing_a_packet(tmp_path, capsys):
    plan_path = write_plan(tmp_path)

    assert main(["check", str(plan_path)]) == 0

    output = capsys.readouterr().out
    assert "DECLARED — CAPTURE, TECHNICAL, CONSENT, AND DELIVERY STATUS UNVERIFIED" in output
    assert not (tmp_path / "packet").exists()


def test_build_writes_packet_and_refuses_a_second_build(tmp_path, capsys):
    plan_path = write_plan(tmp_path)
    output = tmp_path / "packet"

    assert main(["build", str(plan_path), "--output", str(output)]) == 0
    assert (output / "CAPTURE_SHEET.md").is_file()
    assert main(["build", str(plan_path), "--output", str(output)]) == 1
    assert "already exists" in capsys.readouterr().err


def test_invalid_plan_returns_a_concise_nonzero_error(tmp_path, capsys):
    plan_path = tmp_path / "invalid.toml"
    plan_path.write_text('[session]\ntitle = "Missing declared fields"\n', encoding="utf-8")

    assert main(["check", str(plan_path)]) == 1
    assert capsys.readouterr().err.startswith("error:")
