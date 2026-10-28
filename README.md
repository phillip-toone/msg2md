# msg2md

`msg2md` is a small Python command-line utility that converts **one Microsoft Outlook `.msg` email** into **one human-readable Markdown (`.md`) file** alongside the original. It is a converter, not a summarizer or records-management system.

The `.msg` remains the authoritative source. The generated Markdown is a readable derivative suitable for review and project archives; it is not a pixel-perfect reproduction of Outlook.

## Status

**v0.1 implementation — final validation in progress.** The converter has passed 21 automated tests and has been exercised on real Outlook messages. Real-world attachment handling and unusual MSG structures still warrant additional testing.

## Features

- Accepts one `.msg` path per invocation, including paths containing spaces.
- Writes UTF-8 Markdown next to the input using the same filename stem.
- Includes available Subject, From, To, Cc, and Date fields; missing values appear as `Not available`.
- Prefers the plain-text body; converts HTML-only bodies to Markdown when possible, retaining readable text, links, and lists.
- Includes signatures and quoted replies as supplied by the extracted body.
- Lists attachment filenames without saving attachment contents; unnamed attachments receive a neutral description.
- Escapes Markdown-sensitive characters in metadata and attachment names.
- **By default, collapses repeated blank lines** in the derived message body to one blank line, including whitespace-only lines and Windows line endings. This intentionally changes whitespace in the output, not the original email.
- Refuses to overwrite an existing `.md` file and returns a nonzero exit status on failure.
- Runs locally, with no LLM, API key, cloud upload, or network service required for conversion.

## Requirements

- Python with `extract-msg` and `markdownify` installed. Beautiful Soup is used for HTML decoding and is installed as a dependency.
- Development has been tested on **Windows, Git Bash, and Python 3.13.18** using `uv`.

## Installation (Windows / Git Bash)

Clone the repository if needed:

```bash
git clone https://github.com/phillip-toone/msg2md.git
cd msg2md
```

Install [uv](https://docs.astral.sh/uv/) if it is not already available. Create a project environment and install dependencies:

```bash
uv venv --python 3.13 .venv
uv pip install --python .venv/Scripts/python.exe extract-msg markdownify
```

Verify the installation:

```bash
.venv/Scripts/python.exe -c "import extract_msg, markdownify; print('Dependencies OK')"
```

Alternatively, in a conventional Python environment with pip available, install the dependencies using `python -m pip install extract-msg markdownify`. The Windows embeddable Python distribution may not include `pip` or `venv`; a `uv`-managed environment avoids that limitation.

## Usage

From the repository directory:

```bash
.venv/Scripts/python.exe msg2md.py "/d/projects/correspondence/example.msg"
```

This creates `/d/projects/correspondence/example.md` without changing `example.msg`. If `example.md` already exists, the command fails rather than replacing it.

To see CLI help:

```bash
.venv/Scripts/python.exe msg2md.py --help
```

### Optional Git Bash launcher

For use from any Git Bash directory, create an executable launcher named `msg2md` in a directory already on your `PATH`. For the tested portable setup, the launcher is `/d/bin/msg2md` and contains:

```bash
#!/usr/bin/env bash
exec /d/projects/msg2md/.venv/Scripts/python.exe \
     /d/projects/msg2md/msg2md.py "$@"
```

Make it executable with `chmod +x /d/bin/msg2md`. Then, from any Git Bash directory, run:

```bash
msg2md "example.msg"
msg2md "/d/projects/another-repository/correspondence/example.msg"
```

The launcher uses the **current source code** in `/d/projects/msg2md`, including uncommitted changes. Update its paths if the repository moves. This launcher is for Git Bash; it does not automatically add a command to PowerShell or Command Prompt.

## Output format

Each generated document has **Metadata**, **Body**, and **Attachments** sections. Metadata is not invented when missing. Attachments are named but not extracted; the section displays `None` when no attachments are reported.

The original plain-text body is preferred. Excessive blank lines are normalized in the output by default, while ordinary line breaks are retained. Existing Markdown output is never silently regenerated or overwritten.

## Tests

Run the automated suite from the repository directory:

```bash
.venv/Scripts/python.exe -m unittest -v test_msg2md
```

At the time of this documentation update, **21 automated tests passed**, covering input validation, metadata, plain-text and HTML conversion, Windows-1252 HTML, attachment names, Unicode and quoted text, Markdown escaping, blank-line normalization, output protection, simulated write failures, and CLI error handling.

The converter has also been exercised on real `.msg` files. A temporary-copy integration check verified that the input bytes were unchanged after conversion. The automated suite primarily uses mocks and synthetic data; it does not prove compatibility with every Outlook message variant.

**Do not commit real correspondence or sensitive generated Markdown as test fixtures.** A `.gitignore` in this repository does not protect files created inside another repository.

## Safety and limitations

- The input `.msg` is never intentionally modified, moved, or deleted. The output is created only after extraction and conversion have succeeded.
- Existing output is protected against overwrite. Ordinary write failures are tested for cleanup, but a crash, power loss, or unusual filesystem failure may leave a partial output file.
- HTML conversion is best-effort: complex layouts, embedded objects, and uncertain character encodings may not reproduce perfectly.
- Some plain-text content that resembles Markdown syntax may be interpreted as formatting by Markdown viewers. The converter does not rewrite the body to avoid that interpretation.
- The generated Markdown intentionally normalizes excess blank lines, so it is not byte-for-byte identical to the extracted body.
- Attachment contents are not extracted. Real MSG files with attachments, especially embedded Outlook items, require further validation.
- The tool does not automatically commit or push files to Git.

## Scope

v0.1 converts one file per invocation. Batch processing, attachment extraction, Outlook integration, a graphical interface, configuration systems, Git automation, and LLM-generated summaries are deferred.

See [REQUIREMENTS.md](REQUIREMENTS.md) for authoritative functional requirements and [AGENTS.md](AGENTS.md) for development instructions.
