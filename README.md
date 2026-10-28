# msg2md

A small Python command-line utility for converting Microsoft Outlook `.msg` emails into readable Markdown (`.md`) files. The resulting files are intended for human review, Git-based project archives, and later analysis by language models.

## Project status

**Planning / not yet implemented.** The first development task is to implement the single-message converter described in [REQUIREMENTS.md](REQUIREMENTS.md).

## Intended usage

From Git Bash on Windows:

```bash
python msg2md.py "path/to/email.msg"
```

This should create `path/to/email.md` alongside the original. The source `.msg` must remain unchanged. An existing `.md` must not be overwritten.

## Preservation principles

- The `.msg` is the authoritative archived email; Markdown is a derived, readable representation.
- Conversion must preserve message content rather than summarize, paraphrase, or interpret it.
- Signatures and quoted prior messages should remain in the output when present in the source body.
- Attachments should be listed, not extracted.
- The tool should run locally without an LLM or network service.
- Do not commit real correspondence or confidential information to this utility's repository.

## Development

Read [REQUIREMENTS.md](REQUIREMENTS.md) for scope and acceptance criteria and [AGENTS.md](AGENTS.md) for development guidance. Installation and usage instructions will be expanded after implementation.

## License

See [LICENSE](LICENSE).
