
"""Convert one Outlook .msg email to Markdown."""

import argparse
import os
from pathlib import Path

import extract_msg


def convert_message(source: Path) -> Path:
    """Convert one MSG file without modifying the source."""

    if not source.is_file():
        raise ValueError(f"Input file does not exist: {source}")

    if source.suffix.lower() != ".msg":
        raise ValueError("Input must be a .msg file")

    destination = source.with_suffix(".md")

    if destination.exists():
        raise FileExistsError(
            f"Output already exists: {destination}"
        )

    with extract_msg.Message(str(source)) as message:
        body = message.body

        if body is None or not body.strip():
            raise ValueError(
                "No readable plain-text message body found"
            )

        subject = message.subject or "Not available"
        sender = message.sender or "Not available"
        recipients = message.to or "Not available"
        cc = message.cc or "Not available"
        date = message.date or "Not available"

    markdown = (
        "# Email\n\n"
        "## Metadata\n\n"
        f"**Subject:** {subject}\n\n"
        f"**From:** {sender}\n\n"
        f"**To:** {recipients}\n\n"
        f"**Cc:** {cc}\n\n"
        f"**Date:** {date}\n\n"
        "## Body\n\n"
        f"{body}\n"
    )


    fd = os.open(
        destination,
        os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_BINARY,
    )

    try:
        try:
            output = os.fdopen(fd, "w", encoding="utf-8")
        except BaseException:
            os.close(fd)
            raise

        with output:
            output.write(markdown)
    except BaseException:
        destination.unlink()
        raise

    return destination


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Convert one Outlook MSG file to Markdown."
    )
    parser.add_argument(
        "message",
        type=Path,
        help="Path to the Outlook .msg file",
    )

    args = parser.parse_args()

    try:
        destination = convert_message(args.message)
    except (OSError, ValueError, Exception) as error:
        print(f"Error: {error}")
        return 1

    print(f"Created: {destination}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
