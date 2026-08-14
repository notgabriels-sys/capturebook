"""Declared recording-session plan parsing expectations."""

from __future__ import annotations

import pytest

from capturebook.config import ConfigError, load_plan
from tests.helpers import plan_text, write_plan


def test_loads_declared_session_context_and_ordered_input_rows(tmp_path):
    plan_path = write_plan(tmp_path)

    plan = load_plan(plan_path)

    assert plan.source_path == plan_path.resolve()
    assert plan.session.title == "Synthetic Capture Study"
    assert plan.session.sample_rate_hz == 48000
    assert plan.session.bit_depth == 24
    assert [
        (channel.id, channel.input_number, channel.phantom_power, channel.record_route)
        for channel in plan.inputs
    ] == [
        ("kick", 1, False, "Drums"),
        ("voice", 2, True, "Voice"),
        ("texture", 5, False, "Textures"),
    ]


def test_rejects_duplicate_declared_interface_input_numbers(tmp_path):
    plan_path = tmp_path / "duplicate-input.toml"
    plan_path.write_text(
        plan_text().replace("input_number = 5", "input_number = 2"),
        encoding="utf-8",
    )

    with pytest.raises(ConfigError, match="duplicate input number"):
        load_plan(plan_path)


def test_rejects_a_nonpositive_declared_interface_input_number(tmp_path):
    plan_path = tmp_path / "zero-input.toml"
    plan_path.write_text(
        plan_text().replace("input_number = 1", "input_number = 0", 1),
        encoding="utf-8",
    )

    with pytest.raises(ConfigError, match="positive integer"):
        load_plan(plan_path)


def test_rejects_a_nonpositive_declared_sample_rate(tmp_path):
    plan_path = tmp_path / "zero-rate.toml"
    plan_path.write_text(
        plan_text().replace("sample_rate_hz = 48000", "sample_rate_hz = 0"),
        encoding="utf-8",
    )

    with pytest.raises(ConfigError, match="positive integer"):
        load_plan(plan_path)


def test_rejects_an_untracked_top_level_field(tmp_path):
    plan_path = tmp_path / "untracked.toml"
    plan_path.write_text(
        plan_text().replace("[session]\n", 'untracked = "no"\n\n[session]\n', 1),
        encoding="utf-8",
    )

    with pytest.raises(ConfigError, match="unexpected top-level"):
        load_plan(plan_path)


def test_rejects_a_plan_without_declared_session_context(tmp_path):
    plan_path = tmp_path / "missing-session.toml"
    plan_path.write_text(
        """[[inputs]]
id = "orphan"
label = "Orphan"
source = "Synthetic source"
input_number = 1
phantom_power = false
record_route = "Route"
notes = "Synthetic."
""",
        encoding="utf-8",
    )

    with pytest.raises(ConfigError, match="session"):
        load_plan(plan_path)


def test_rejects_an_empty_declared_inputs_list(tmp_path):
    plan_path = tmp_path / "empty-inputs.toml"
    plan_path.write_text(
        "inputs = []\n\n" + plan_text().split("[[inputs]]", maxsplit=1)[0],
        encoding="utf-8",
    )

    with pytest.raises(ConfigError, match="nonempty"):
        load_plan(plan_path)


def test_rejects_an_untracked_declared_session_field(tmp_path):
    plan_path = tmp_path / "untracked-session.toml"
    plan_path.write_text(
        plan_text().replace(
            'title = "Synthetic Capture Study"',
            'title = "Synthetic Capture Study"\nextra = "oops"',
        ),
        encoding="utf-8",
    )

    with pytest.raises(ConfigError, match="unexpected session"):
        load_plan(plan_path)


def test_rejects_an_untracked_declared_input_field(tmp_path):
    plan_path = tmp_path / "untracked-input.toml"
    plan_path.write_text(
        plan_text().replace('label = "Kick"', 'label = "Kick"\nextra = "oops"', 1),
        encoding="utf-8",
    )

    with pytest.raises(ConfigError, match="unexpected inputs\\[1\\]"):
        load_plan(plan_path)


def test_rejects_duplicate_declared_input_ids(tmp_path):
    plan_path = tmp_path / "duplicate-id.toml"
    plan_path.write_text(
        plan_text().replace('id = "texture"', 'id = "voice"'),
        encoding="utf-8",
    )

    with pytest.raises(ConfigError, match="duplicate input id"):
        load_plan(plan_path)


def test_rejects_a_nonboolean_declared_phantom_power_field(tmp_path):
    plan_path = tmp_path / "invalid-phantom.toml"
    plan_path.write_text(
        plan_text().replace("phantom_power = false", 'phantom_power = "maybe"', 1),
        encoding="utf-8",
    )

    with pytest.raises(ConfigError, match="Boolean"):
        load_plan(plan_path)


def test_rejects_a_missing_required_session_field_with_a_controlled_error(tmp_path):
    plan_path = tmp_path / "missing-bit-depth.toml"
    plan_path.write_text(
        plan_text().replace("bit_depth = 24\n", ""),
        encoding="utf-8",
    )

    with pytest.raises(ConfigError, match="session.bit_depth"):
        load_plan(plan_path)
