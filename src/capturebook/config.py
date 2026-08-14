"""Parse declared recording-session preparation plans into typed session and input facts."""

from __future__ import annotations

import tomllib
from dataclasses import dataclass
from pathlib import Path


class ConfigError(ValueError):
    """Raised when a declared capture plan is incomplete or ambiguous."""


@dataclass(frozen=True)
class Session:
    """Declared context; it does not verify a session, capture, consent, or delivery."""

    title: str
    date_label: str
    sample_rate_hz: int
    bit_depth: int
    review_note: str


@dataclass(frozen=True)
class InputChannel:
    """One declared channel-preparation row, not evidence of a physical connection."""

    id: str
    label: str
    source: str
    input_number: int
    phantom_power: bool
    record_route: str
    notes: str


@dataclass(frozen=True)
class CapturePlan:
    """A local declared plan with no observation of the actual recording session."""

    source_path: Path
    session: Session
    inputs: tuple[InputChannel, ...]


def load_plan(path: Path) -> CapturePlan:
    """Load one declared TOML capture plan in the exact shape Capturebook currently needs."""

    source_path = path.resolve()
    raw = tomllib.loads(source_path.read_text(encoding="utf-8"))
    unknown_top_level_fields = sorted(set(raw) - {"session", "inputs"})
    if unknown_top_level_fields:
        raise ConfigError(f"unexpected top-level field(s): {', '.join(unknown_top_level_fields)}")
    if "session" not in raw or "inputs" not in raw:
        raise ConfigError("capture plan must contain [session] and at least one [[inputs]] table")
    session = raw["session"]
    allowed_session_fields = {
        "title",
        "date_label",
        "sample_rate_hz",
        "bit_depth",
        "review_note",
    }
    unknown_session_fields = sorted(set(session) - allowed_session_fields)
    if unknown_session_fields:
        raise ConfigError(f"unexpected session field(s): {', '.join(unknown_session_fields)}")
    for field in ("title", "date_label", "sample_rate_hz", "bit_depth", "review_note"):
        if field not in session:
            raise ConfigError(f"session.{field} is required")
    sample_rate_hz = session["sample_rate_hz"]
    bit_depth = session["bit_depth"]
    for field, value in (("sample_rate_hz", sample_rate_hz), ("bit_depth", bit_depth)):
        if not isinstance(value, int) or isinstance(value, bool) or value <= 0:
            raise ConfigError(f"session.{field} must be a positive integer")
    inputs = raw["inputs"]
    if not isinstance(inputs, list) or not inputs:
        raise ConfigError("inputs must be a nonempty TOML array")
    allowed_input_fields = {
        "id",
        "label",
        "source",
        "input_number",
        "phantom_power",
        "record_route",
        "notes",
    }
    input_numbers: set[int] = set()
    input_ids: set[str] = set()
    for index, channel in enumerate(inputs, start=1):
        unknown_input_fields = sorted(set(channel) - allowed_input_fields)
        if unknown_input_fields:
            raise ConfigError(
                f"unexpected inputs[{index}] field(s): {', '.join(unknown_input_fields)}"
            )
        if channel["id"] in input_ids:
            raise ConfigError(f"duplicate input id: {channel['id']}")
        input_ids.add(channel["id"])
        if not isinstance(channel["phantom_power"], bool):
            raise ConfigError(f"inputs[{index}].phantom_power must be a Boolean")
        input_number = channel["input_number"]
        if not isinstance(input_number, int) or isinstance(input_number, bool) or input_number <= 0:
            raise ConfigError(f"inputs[{index}].input_number must be a positive integer")
        if input_number in input_numbers:
            raise ConfigError(f"duplicate input number: {input_number}")
        input_numbers.add(input_number)
    return CapturePlan(
        source_path=source_path,
        session=Session(
            title=session["title"],
            date_label=session["date_label"],
            sample_rate_hz=sample_rate_hz,
            bit_depth=bit_depth,
            review_note=session["review_note"],
        ),
        inputs=tuple(
            InputChannel(
                id=channel["id"],
                label=channel["label"],
                source=channel["source"],
                input_number=channel["input_number"],
                phantom_power=channel["phantom_power"],
                record_route=channel["record_route"],
                notes=channel["notes"],
            )
            for channel in inputs
        ),
    )
