# Packet method

Capturebook parses a local TOML plan and records the declared session and input fields into a Markdown sheet and CSV table. It writes a separate manifest containing the plan filename, plan SHA-256, generated-file byte counts, and generated-file SHA-256 values.

The program never modifies the declared source plan. It does not open or create audio files, interact with recording hardware, or send a session request elsewhere. Build refuses an existing output directory so an earlier packet cannot be overwritten unintentionally.

The sheet preserves input rows in the declared TOML order. Each CSV phantom_power value is rendered as declared_on or declared_off rather than a plain hardware assertion. The output is preparation material that supports review; it is not a log of observed technical state or a capture report.

Hash values prove only which local input and generated packet bytes were present for that run. They do not prove rights, consent, source identity, physical connection, a successful take, backup, approval, or delivery.
