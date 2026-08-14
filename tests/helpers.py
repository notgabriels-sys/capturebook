"""Small fictional recording-session fixtures for Capturebook behavior tests."""

from __future__ import annotations

from pathlib import Path


def plan_text() -> str:
    """Return one fictional three-input recording-session plan."""

    return """[session]
title = "Synthetic Capture Study"
date_label = "Fictional session date"
sample_rate_hz = 48000
bit_depth = 24
review_note = "Synthetic test plan only; all further facts remain unverified."

[[inputs]]
id = "kick"
label = "Kick"
source = "Synthetic kick source"
input_number = 1
phantom_power = false
record_route = "Drums"
notes = "Confirm source and routing before capture."

[[inputs]]
id = "voice"
label = "Voice"
source = "Synthetic voice source"
input_number = 2
phantom_power = true
record_route = "Voice"
notes = "Confirm source, consent, and routing before capture."

[[inputs]]
id = "texture"
label = "Texture"
source = "Synthetic texture source"
input_number = 5
phantom_power = false
record_route = "Textures"
notes = "Confirm source and routing before capture."
"""


def write_plan(tmp_path: Path, name: str = "capturebook.toml") -> Path:
    """Write one fictional declared capture plan."""

    path = tmp_path / name
    path.write_text(plan_text(), encoding="utf-8")
    return path
