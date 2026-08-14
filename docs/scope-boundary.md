# Scope boundary

Capturebook is intentionally a written-plan tool. It consumes a local TOML declaration and produces a preparation sheet and CSV. It has no audio interface, recorder, DAW, hardware-control, backup, consent, delivery, or network integration.

| Question | What Capturebook can record | What remains unverified |
| --- | --- | --- |
| What plan was used? | Local filename and SHA-256 | Authorship, approval, source provenance outside the declared local plan |
| Which rows are declared? | IDs, input numbers, labels, sources, routes, notes, and declared phantom values | Physical source identity, device connection, patching, routing, device state |
| Is phantom power safe or active? | Only the declared Boolean rendered as declared_on or declared_off | Microphone/device compatibility, electrical state, safe operation, actual switch state |
| Did a session happen? | Nothing | Consent, recording, takes, file paths, quality, backup, attendance, session result |
| Was it delivered? | Nothing | Client approval, files, checksum handoff, billing, delivery or release outcome |

The terminal and packet state is always **DECLARED — CAPTURE, TECHNICAL, CONSENT, AND DELIVERY STATUS UNVERIFIED**. This visible boundary stops a well-formatted sheet from being mistaken for a technical log or a completed recording record.

For any real session, verify facts in the actual room and equipment context. Keep session files, consent/approval records, take logs, backup verification, and delivery evidence in their own source-backed workflow.
