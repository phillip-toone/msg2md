# Instructions for AI Coding Assistants

Read `README.md` and `REQUIREMENTS.md` before proposing or making changes. `REQUIREMENTS.md` is authoritative for the initial scope. These documents are the project handoff; no prior chat is required.

## Objective

Implement `msg2md`, a small Python CLI that converts a single Outlook `.msg` email to a faithful, human-readable Markdown file alongside the original.

## Development principles

- Prefer the simplest maintainable solution that satisfies the requirements.
- Preserve original message content; never summarize, paraphrase, or invent information during conversion.
- Never modify the original `.msg` or overwrite an existing `.md`.
- Use established parsing libraries rather than implementing the MSG binary format manually.
- Handle errors clearly, especially partial extraction and unsupported message structures.
- Keep processing local; do not add LLM integration, APIs, telemetry, or network services.
- Do not commit real emails, sensitive correspondence, credentials, or personal records. Use synthetic or sanitized fixtures for testing.
- Add automated tests for successful conversion and safety/failure cases.
- Update `README.md` with installation and usage instructions once implementation exists.
- Keep Git commits focused and explain what changed and why.

## Workflow

1. Review the requirements and propose a minimal implementation and testing approach.
2. Implement the converter without adding deferred features.
3. Test it using synthetic or sanitized fixtures, including HTML-only and error cases where practical.
4. Review output fidelity and ensure the source is never modified.
5. Document dependencies, usage, limitations, and test results.

Ask before making scope-expanding architectural changes. Do not assume access to earlier conversations.

## Current development baseline (2026-10-28)

- Core implementation: `msg2md.py`; tests: `test_msg2md.py`. The initial implementation and compact-blank-line behavior are in place, but final v0.1 acceptance is still pending.
- Tested environment: Windows with Git Bash, uv-managed Python 3.13.18, and a project-local `.venv` containing `extract-msg` and `markdownify` (Beautiful Soup is installed as a dependency).
- From the repository root, run tests with `.venv/Scripts/python.exe -m unittest -v test_msg2md`. At this checkpoint, 21 tests pass.
- Run a conversion with `.venv/Scripts/python.exe msg2md.py "path/to/message.msg"`. An optional local Git Bash launcher at `/d/bin/msg2md` invokes this same script and virtual environment. Do not assume the launcher exists on other machines.
- Output is written beside the `.msg`, refuses overwrites, and normalizes repeated blank lines by default. This intentional change applies to the derived Markdown body, not the source email. Refer to `REQUIREMENTS.md` for the precise scope.
- Tests use mocks and synthetic data. Real-format integration testing has covered several messages and a source-integrity check, but real attachments and unusual embedded Outlook objects still need validation.

## Change and documentation workflow

- Make focused changes with a test or reproducible check, then run the full suite before committing.
- Prefer small, verifiable Git Bash commands for code changes. For complete documentation revisions, provide a full downloadable `.md` file for local review rather than embedding Markdown code fences inside a shell heredoc.
- Before committing, review `git diff --check`, `git diff`, and `git status --short`. Never commit correspondence, generated Markdown containing sensitive information, or temporary preview files.
- Keep `README.md`, `REQUIREMENTS.md`, and `AGENTS.md` consistent. `REQUIREMENTS.md` remains authoritative; describe unverified behavior as pending rather than claiming a release is complete.
- Do not introduce batch processing, LLMs, network services, attachment extraction, or other deferred features without explicit approval.
