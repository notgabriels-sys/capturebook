"""Command-line interface for declared Capturebook session-preparation packets."""

from __future__ import annotations

import argparse
import sys
import tomllib
from collections.abc import Sequence
from pathlib import Path

from capturebook.config import ConfigError, load_plan
from capturebook.report import STATE_LABEL, write_bundle


def build_parser() -> argparse.ArgumentParser:
    """Build the small explicit command surface for reviewing or writing one capture sheet."""

    parser = argparse.ArgumentParser(
        prog="capturebook",
        description="Build declared recording-session preparation sheets without capture claims.",
    )
    commands = parser.add_subparsers(dest="command", required=True)
    check = commands.add_parser(
        "check", help="Parse declared session fields in memory and report their boundary."
    )
    check.add_argument("plan", type=Path, help="Path to a Capturebook TOML plan.")
    build = commands.add_parser("build", help="Write a new CSV-and-Markdown preparation packet.")
    build.add_argument("plan", type=Path, help="Path to a Capturebook TOML plan.")
    build.add_argument(
        "--output", type=Path, required=True, help="New packet directory; must not exist."
    )
    return parser


def check_summary(plan_name: str, input_count: int, sample_rate_hz: int, bit_depth: int) -> str:
    """Return a concise terminal summary that keeps the preparation boundary visible."""

    return "\n".join(
        [
            f"Capture plan: {plan_name}",
            f"State: {STATE_LABEL}",
            f"Declared input rows: {input_count}",
            f"Declared format: {sample_rate_hz} Hz / {bit_depth}-bit",
            "No technical, consent, capture, backup, or delivery claim has been verified.",
        ]
    )


def main(argv: Sequence[str] | None = None) -> int:
    """Run one declared capture-preparation command and return a conventional status code."""

    parser = build_parser()
    arguments = parser.parse_args(argv)
    try:
        plan = load_plan(arguments.plan)
        summary = check_summary(
            plan.source_path.name,
            len(plan.inputs),
            plan.session.sample_rate_hz,
            plan.session.bit_depth,
        )
        if arguments.command == "check":
            print(summary)
            return 0
        bundle = write_bundle(plan, arguments.output)
        print(summary)
        print(f"Wrote preparation packet: {bundle.output_path}")
        return 0
    except (
        ConfigError,
        FileExistsError,
        KeyError,
        OSError,
        ValueError,
        tomllib.TOMLDecodeError,
    ) as error:
        print(f"error: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
