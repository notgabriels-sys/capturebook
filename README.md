# Capturebook

Capturebook turns a written recording-session plan into an offline **preparation packet**: a Markdown capture sheet, spreadsheet-ready CSV input list, and hash manifest. It is intended to make a declared channel layout easier to review before a session, not to turn a technical plan into evidence that a recording happened.

Every successful run carries this state:

> **DECLARED — CAPTURE, TECHNICAL, CONSENT, AND DELIVERY STATUS UNVERIFIED**

Capturebook records only declared plan fields. It does **not** establish source identity, patching, physical connection, phantom-power safety, preamp gain, clocking, consent, capture, take quality, backups, or delivery.

## Install

Capturebook needs Python 3.11+ and has no runtime dependencies beyond the standard library. From a clone:

    python3 -m pip install .

For development:

    python3 -m pip install -e '.[dev]'
    python3 -m pytest -q
    python3 -m ruff check .

It works only with a local TOML plan. It does not connect to an audio interface, DAW, recorder, monitor controller, cloud backup, client account, email, or network service.

## Declare a session plan

This fictional example shows every field. Replacing it with a real project plan does not make any live technical or consent fact verified.

    [session]
    title = "Synthetic Capture Study"
    date_label = "Fictional session date"
    sample_rate_hz = 48000
    bit_depth = 24
    review_note = "Fictional test plan only; all further facts remain unverified."

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

The plan is strict. Its only top-level entries are [session] and one or more [[inputs]] tables. Session fields are title, date_label, sample_rate_hz, bit_depth, and review_note. Input fields are id, label, source, input_number, phantom_power, record_route, and notes.

Input IDs and input numbers must be unique. Sample rate, bit depth, and input number must be positive integers. Phantom power must be a TOML Boolean. These checks describe plan structure only; they do not validate interface compatibility, microphone type, electrical safety, or actual device state.

## Check, then build

Check parses the declared plan in memory, writing nothing:

    capturebook check path/to/capturebook.toml

Build writes a new packet directory and refuses to overwrite one that already exists:

    capturebook build path/to/capturebook.toml --output path/to/capture-prep

The output is deliberately limited to portable preparation records:

    capture-prep/
    ├── CAPTURE_MANIFEST.md
    ├── CAPTURE_SHEET.csv
    └── CAPTURE_SHEET.md

The Markdown sheet holds the declared session context and input rows. The CSV contains one row per declared input. The manifest records the plan filename and SHA-256 plus byte counts and SHA-256 fingerprints for generated records. It does not expose the plan's absolute local path.

## What a phantom-power field means here

The CSV and Markdown outputs use declared_on or declared_off. That wording is intentional: it reflects only what the plan says. It is not a prompt to engage phantom power, a compatibility check, a microphone specification, or proof of the hardware's actual state.

Before any real session, confirm every relevant connection, source, microphone, power requirement, gain, clock, routing, consent, recording path, backup process, and client/artist approval in the actual environment. See [the scope boundary](docs/scope-boundary.md) and [the packet method](docs/packet-method.md) for the precise limits.
