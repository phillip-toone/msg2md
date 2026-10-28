# Requirements — msg2md v0.1

## Objective

Build a simple Python command-line utility that accepts **one** Microsoft Outlook `.msg` file and writes **one** human-readable Markdown file alongside it. The utility is a faithful converter, not an email summarizer or records-management system.

## Command-line interface

```bash
python msg2md.py "path/to/message.msg"
```

- Accept one positional path to an existing `.msg` file. Paths containing spaces must work in Git Bash on Windows.
- Write the Markdown output to the same directory, using the same filename stem and the `.md` extension.
- Provide a concise `--help` message and clear success/failure feedback.
- Return a nonzero exit status on failure.
- Do not overwrite an existing output file. No overwrite option is required in v0.1.

## Conversion

- Extract available metadata: subject, sender, recipients (To and Cc), and date/time.
- Represent missing metadata explicitly and neutrally (for example, `Not available`); do not invent values.
- Preserve the complete readable message text, including signatures and quoted replies as supplied by the source. The derived Markdown may normalize excessive blank lines as described below; do not remove substantive content.
- Prefer a plain-text body when one is available. If the message is HTML-only, convert the HTML to readable Markdown while preserving meaningful text, links, and list structure where practical.
- List attachment filenames, if any, without extracting attachments or embedding their content. Handle unnamed attachments without inventing names.
- Use clear Markdown headings for message metadata, body, and attachments.
- Escape or otherwise safely represent metadata that could disrupt Markdown formatting.
- Preserve Unicode characters using UTF-8 output.
- Do not summarize, rewrite, classify, or add AI-generated notes.
- If the body cannot be extracted reliably, fail clearly rather than silently writing a misleadingly empty or incomplete document. Document any known limitations of extraction, especially HTML layout and embedded objects.

## Readability formatting (v0.1 decision)

- By default, normalize line endings in the derived body to LF and collapse runs of consecutive blank lines (including whitespace-only lines) to one blank line.
- Preserve ordinary single line breaks and all substantive text. Do not summarize or reword the email.
- This is an intentional whitespace transformation in the `.md` output only. The `.msg` remains authoritative and unchanged.
- No formatting option or alternate preservation mode is required in v0.1.

## Safety and scope

- Never modify, move, or delete the input `.msg` file.
- Do not write or overwrite the destination until extraction and conversion have succeeded; use a safe creation strategy to avoid replacing an existing file.
- Operate locally; no network calls, external AI services, telemetry, or cloud uploads.
- Do not execute content found inside an email or load remote HTML resources.
- Avoid printing email bodies or sensitive metadata in routine console output.
- Do not automatically commit or push files to Git.

## Implementation constraints

- Target Python on Windows, invoked from Git Bash.
- Prefer established libraries for Outlook MSG extraction and HTML-to-Markdown conversion; evaluate `extract-msg` as a starting point.
- Keep the first version small and maintainable. A single `msg2md.py` script is acceptable.
- Document installation, dependencies, and usage in `README.md` after implementation.

## Acceptance criteria

1. Given a valid `.msg` with plain-text body and metadata, the tool creates a readable UTF-8 `.md` beside it.
2. The output retains original message text, signatures, and quoted replies when present.
3. An HTML-only message produces readable Markdown or a clear error if faithful extraction is not possible.
4. Attachment names are listed without extracting attachments.
5. Missing optional metadata does not crash the utility or produce fabricated values.
6. A source path containing spaces works.
7. An existing `.md` is never overwritten, and the `.msg` remains unchanged.
8. Invalid, missing, or unsupported inputs produce helpful errors and nonzero exit codes.
9. Automated tests cover normal conversion and important failure cases, using synthetic or sanitized data only.
10. The utility requires no LLM, API key, network access, or Git integration.

## Deferred features

- LLM-generated summaries, decisions, or project notes.
- Batch conversion, directory scanning, or thread-level analysis.
- Extracting or saving attachments.
- Direct Outlook integration, graphical interfaces, configuration systems, and Git automation.

## Implementation and verification status (2026-10-28)

The initial converter is implemented in `msg2md.py` using `extract-msg`, `markdownify`, and Beautiful Soup. Development has been verified on Windows/Git Bash with a uv-managed Python 3.13.18 environment. A Git Bash launcher at `/d/bin/msg2md` is an optional local convenience, not a required installed component.

At this checkpoint, 21 automated tests pass, covering normal and failure paths, HTML fallback, metadata handling, attachments using mocks, whitespace normalization, and output safety. Several real Outlook messages have been converted and reviewed; a temporary-copy integration check verified unchanged source bytes. These results support the implemented behavior but do **not** establish universal compatibility with Outlook variants.

**Remaining acceptance checks before declaring v0.1 released:** test a sanitized real `.msg` containing an attachment, review unusual/embedded attachments and extraction failures, and confirm documentation and output fidelity against representative samples. Do not weaken acceptance criteria to match the implementation.
