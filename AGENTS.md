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
