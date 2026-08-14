"""Write declared Capturebook session-preparation packets in Markdown and CSV."""

from __future__ import annotations

import csv
import hashlib
from dataclasses import dataclass
from pathlib import Path

from capturebook.config import CapturePlan, InputChannel

STATE_LABEL = "DECLARED — CAPTURE, TECHNICAL, CONSENT, AND DELIVERY STATUS UNVERIFIED"


@dataclass(frozen=True)
class CaptureBundle:
    """Paths for a newly written declared recording-session preparation packet."""

    output_path: Path
    markdown_path: Path
    csv_path: Path
    manifest_path: Path
    artifact_paths: tuple[Path, ...]


def sha256_file(path: Path) -> str:
    """Return a streaming SHA-256 fingerprint for one plan or generated artifact."""

    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def phantom_label(channel: InputChannel) -> str:
    """Return the plan's declared phantom-power state without asserting hardware state."""

    return "declared_on" if channel.phantom_power else "declared_off"


def markdown_cell(value: str) -> str:
    """Escape a declared table value so it cannot alter Markdown column structure."""

    return value.replace("\\", "\\\\").replace("|", "\\|").replace("\n", "<br>")


def capture_sheet_markdown(plan: CapturePlan) -> str:
    """Render declared session and channel facts as a preparation sheet, not a capture report."""

    session = plan.session
    lines = [
        "# Capturebook preparation sheet",
        "",
        f"**State:** {STATE_LABEL}",
        "",
        "## Declared session context",
        "",
        f"- Title: {session.title}",
        f"- Date label: {session.date_label}",
        f"- Declared sample rate: {session.sample_rate_hz} Hz",
        f"- Declared bit depth: {session.bit_depth}-bit",
        "",
        "## Declared input sheet",
        "",
        "| Input | ID | Label | Source | Declared phantom power | Record route | Notes |",
        "| ---: | --- | --- | --- | --- | --- | --- |",
    ]
    for channel in plan.inputs:
        lines.append(
            f"| {channel.input_number} | {markdown_cell(channel.id)} | "
            f"{markdown_cell(channel.label)} | {markdown_cell(channel.source)} | "
            f"{phantom_label(channel)} | {markdown_cell(channel.record_route)} | "
            f"{markdown_cell(channel.notes)} |"
        )
    lines.extend(
        [
            "",
            "## Preparation boundary",
            "",
            "This sheet records only declared preparation fields. "
            "It does not establish source identity, physical connection, patching, "
            "phantom-power safety, preamp gain, clocking, file naming, consent, "
            "recording, take quality, backup, or delivery. "
            "Review note supplied in the plan:",
            "",
            f"> {session.review_note}",
            "",
        ]
    )
    return "\n".join(lines)


def write_csv(plan: CapturePlan, path: Path) -> None:
    """Write spreadsheet-ready declared channel facts without changing the local plan."""

    fields = [
        "id",
        "label",
        "source",
        "input_number",
        "phantom_power",
        "record_route",
        "notes",
    ]
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for channel in plan.inputs:
            writer.writerow(
                {
                    "id": channel.id,
                    "label": channel.label,
                    "source": channel.source,
                    "input_number": channel.input_number,
                    "phantom_power": phantom_label(channel),
                    "record_route": channel.record_route,
                    "notes": channel.notes,
                }
            )


def manifest_markdown(plan: CapturePlan, artifacts: tuple[Path, ...]) -> str:
    """Record plan and artifact fingerprints without revealing the absolute plan path."""

    session = plan.session
    lines = [
        "# Capturebook manifest",
        "",
        f"**State:** {STATE_LABEL}",
        "",
        "This packet records declared preparation inputs and generated review artifacts. "
        "It does not establish technical, consent, capture, backup, or delivery status.",
        "",
        "## Declared plan facts",
        "",
        f"- Plan file name: {plan.source_path.name}",
        f"- Plan SHA-256: {sha256_file(plan.source_path)}",
        f"- Declared session title: {session.title}",
        f"- Declared format: {session.sample_rate_hz} Hz / {session.bit_depth}-bit",
        f"- Declared input rows: {len(plan.inputs)}",
        "",
        "## Generated artifacts",
        "",
        "| File | Bytes | SHA-256 |",
        "| --- | ---: | --- |",
    ]
    for artifact in artifacts:
        lines.append(f"| {artifact.name} | {artifact.stat().st_size} | {sha256_file(artifact)} |")
    lines.append("")
    return "\n".join(lines)


def write_bundle(plan: CapturePlan, output_path: Path) -> CaptureBundle:
    """Write a new preparation packet, refusing to overwrite an existing output directory."""

    output_path = output_path.resolve()
    if output_path.exists():
        raise FileExistsError(f"output packet already exists: {output_path}")
    output_path.mkdir(parents=True)
    markdown_path = output_path / "CAPTURE_SHEET.md"
    markdown_path.write_text(capture_sheet_markdown(plan), encoding="utf-8")
    csv_path = output_path / "CAPTURE_SHEET.csv"
    write_csv(plan, csv_path)
    artifact_paths = (markdown_path, csv_path)
    manifest_path = output_path / "CAPTURE_MANIFEST.md"
    manifest_path.write_text(manifest_markdown(plan, artifact_paths), encoding="utf-8")
    return CaptureBundle(
        output_path=output_path,
        markdown_path=markdown_path,
        csv_path=csv_path,
        manifest_path=manifest_path,
        artifact_paths=artifact_paths,
    )
