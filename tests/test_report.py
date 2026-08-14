"""Capture-sheet packet and source-boundary expectations."""

from __future__ import annotations

import csv
import hashlib

import pytest

from capturebook.config import load_plan
from capturebook.report import write_bundle
from tests.helpers import plan_text, write_plan


def test_writes_hashed_markdown_and_csv_packet_without_exposing_absolute_plan_path(tmp_path):
    plan_path = write_plan(tmp_path)
    before = plan_path.read_bytes()
    plan = load_plan(plan_path)

    bundle = write_bundle(plan, tmp_path / "packet")

    assert plan_path.read_bytes() == before
    assert {entry.name for entry in bundle.output_path.iterdir()} == {
        "CAPTURE_MANIFEST.md",
        "CAPTURE_SHEET.csv",
        "CAPTURE_SHEET.md",
    }
    manifest = bundle.manifest_path.read_text(encoding="utf-8")
    assert "DECLARED — CAPTURE, TECHNICAL, CONSENT, AND DELIVERY STATUS UNVERIFIED" in manifest
    assert str(plan_path) not in manifest
    for artifact in bundle.artifact_paths:
        digest = hashlib.sha256(artifact.read_bytes()).hexdigest()
        assert digest in manifest
    with bundle.csv_path.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    assert [(row["id"], row["input_number"], row["phantom_power"]) for row in rows] == [
        ("kick", "1", "declared_off"),
        ("voice", "2", "declared_on"),
        ("texture", "5", "declared_off"),
    ]


def test_refuses_to_overwrite_an_existing_capture_sheet_packet(tmp_path):
    output = tmp_path / "packet"
    write_bundle(load_plan(write_plan(tmp_path)), output)

    with pytest.raises(FileExistsError, match="already exists"):
        write_bundle(load_plan(write_plan(tmp_path)), output)


def test_escapes_declared_table_text_that_contains_a_markdown_pipe(tmp_path):
    plan_path = tmp_path / "pipe-note.toml"
    plan_path.write_text(
        plan_text().replace(
            'notes = "Confirm source and routing before capture."',
            'notes = "Synthetic | note"',
            1,
        ),
        encoding="utf-8",
    )

    bundle = write_bundle(load_plan(plan_path), tmp_path / "packet")

    assert "Synthetic \\| note" in bundle.markdown_path.read_text(encoding="utf-8")
