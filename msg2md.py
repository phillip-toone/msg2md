
"""Convert one Outlook .msg email to Markdown."""

import argparse
import os
import re
from pathlib import Path

import extract_msg
from bs4 import BeautifulSoup
from markdownify import markdownify


def escape_markdown(value: str) -> str:
    """Escape Markdown syntax in metadata and filenames."""
    value = str(value)
    value = value.replace("\r", " ").replace("\n", " ")
    return re.sub(
        r"([\\`*_\[\]<>|])",
        lambda match: "\\" + match.group(1),
        value,
    )


def normalize_blank_lines(text: str) -> str:
    """Collapse consecutive blank lines to one."""
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    return re.sub(r"\n(?:[ \t]*\n)+", "\n\n", text)


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
            html = message.htmlBody

            if html:
                if isinstance(html, bytes):
                    soup = BeautifulSoup(html, "html.parser")
                    html = str(soup)

                body = markdownify(
                    html,
                    heading_style="ATX",
                )

            if body is None or not body.strip():
                raise ValueError(
                    "No readable message body found"
                )

        body = normalize_blank_lines(body)

        subject = message.subject or "Not available"
        sender = message.sender or "Not available"
        recipients = message.to or "Not available"
        cc = message.cc or "Not available"
        date = message.date or "Not available"

        attachment_names = []
        for attachment in message.attachments:
            filename = (
                attachment.longFilename
                or attachment.shortFilename
            )
            attachment_names.append(filename)

    markdown = (
        "# Email\n\n"
        "## Metadata\n\n"
        f"**Subject:** {escape_markdown(subject)}\n\n"
        f"**From:** {escape_markdown(sender)}\n\n"
        f"**To:** {escape_markdown(recipients)}\n\n"
        f"**Cc:** {escape_markdown(cc)}\n\n"
        f"**Date:** {escape_markdown(date)}\n\n"
        "## Body\n\n"
        f"{body}\n"
    )


    markdown += "\n## Attachments\n\n"

    if attachment_names:
        for filename in attachment_names:
            if filename:
                markdown += f"- {escape_markdown(filename)}\n"
            else:
                markdown += "- Unnamed attachment\n"
    else:
        markdown += "None\n"

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
    except FileExistsError:
        print("Error: Output Markdown file already exists.")
        return 1
    except ValueError as error:
        message = str(error)

        if message.startswith("Input file does not exist:"):
            print("Error: Input file does not exist.")
        elif message == "Input must be a .msg file":
            print("Error: Input must be a .msg file.")
        elif message == "No readable message body found":
            print("Error: No readable message body found.")
        else:
            print("Error: Message conversion failed.")
        return 1
    except OSError:
        print("Error: File access or writing failed.")
        return 1
    except Exception:
        print("Error: Message conversion failed.")
        return 1

    print(f"Created: {destination}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
