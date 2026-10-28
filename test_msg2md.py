
"""Automated tests for the msg2md converter."""

import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

from msg2md import convert_message


class TestMsg2Md(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp_dir.cleanup)
        self.directory = Path(self.temp_dir.name)

    def make_source(self, filename="test.msg"):
        """Create a synthetic placeholder MSG file."""
        source = self.directory / filename
        source.write_bytes(b"synthetic MSG placeholder")
        return source

    def mock_message(self, **overrides):
        """Create a simulated Outlook message."""
        values = {
            "subject": "Test Subject",
            "sender": "Alice <alice@example.com>",
            "to": "Bob <bob@example.com>",
            "cc": None,
            "date": "2026-10-28 09:30",
            "htmlBody": None,
            "attachments": [],
            "body": (
                "Hello Bob,\n\n"
                "This is a test message.\n\n"
                "Regards,\nAlice"
            ),
        }
        values.update(overrides)

        message = MagicMock()
        for name, value in values.items():
            setattr(message, name, value)

        # Support use as a context manager.
        message.__enter__.return_value = message
        message.__exit__.return_value = False

        return message

    def test_missing_input(self):
        source = self.directory / "missing.msg"

        with self.assertRaises(ValueError):
            convert_message(source)

        self.assertFalse(source.with_suffix(".md").exists())

    def test_invalid_extension(self):
        source = self.make_source("test.txt")

        with self.assertRaises(ValueError):
            convert_message(source)

        self.assertFalse(source.with_suffix(".md").exists())

    def test_existing_output_is_not_overwritten(self):
        source = self.make_source()
        destination = source.with_suffix(".md")
        original_output = b"Existing content\r\n"
        destination.write_bytes(original_output)
        original_source = source.read_bytes()

        with self.assertRaises(FileExistsError):
            convert_message(source)

        self.assertEqual(
            destination.read_bytes(),
            original_output,
        )
        self.assertEqual(
            source.read_bytes(),
            original_source,
        )

    @patch("msg2md.extract_msg.Message")
    def test_plain_text_conversion(self, mock_message_class):
        source = self.make_source()
        original_bytes = source.read_bytes()

        mock_message_class.return_value = self.mock_message()

        destination = convert_message(source)

        self.assertTrue(destination.exists())
        self.assertEqual(source.read_bytes(), original_bytes)

        content = destination.read_text(encoding="utf-8")

        self.assertIn("**Subject:** Test Subject", content)
        self.assertIn("**From:** Alice", content)
        self.assertIn("**To:** Bob", content)
        self.assertIn("## Body", content)
        self.assertIn("Hello Bob,", content)
        self.assertIn("This is a test message.", content)
        self.assertIn("Regards,\nAlice", content)

    @patch("msg2md.extract_msg.Message")
    def test_missing_optional_metadata(self, mock_message_class):
        source = self.make_source()

        mock_message_class.return_value = self.mock_message(
            subject=None,
            sender=None,
            to=None,
            cc=None,
            date=None,
        )

        destination = convert_message(source)
        content = destination.read_text(encoding="utf-8")

        self.assertEqual(
            content.count("Not available"),
            5,
        )

    @patch("msg2md.extract_msg.Message")
    def test_missing_body_fails(self, mock_message_class):
        source = self.make_source()

        mock_message_class.return_value = self.mock_message(
            body=None,
        )

        with self.assertRaises(ValueError):
            convert_message(source)

        self.assertFalse(source.with_suffix(".md").exists())


    @patch("msg2md.extract_msg.Message")
    def test_write_failure_removes_partial_output(
        self, mock_message_class
    ):
        source = self.make_source()
        mock_message_class.return_value = self.mock_message()

        destination = source.with_suffix(".md")
        original_bytes = source.read_bytes()

        import os

        original_fdopen = os.fdopen

        class FailingWriter:
            def __init__(self, stream):
                self.stream = stream

            def __enter__(self):
                return self

            def __exit__(self, exc_type, exc_value, traceback):
                return self.stream.__exit__(
                    exc_type, exc_value, traceback
                )

            def write(self, text):
                self.stream.write("Partial output")
                raise OSError("Simulated write failure")

        def failing_fdopen(fd, *args, **kwargs):
            return FailingWriter(
                original_fdopen(fd, *args, **kwargs)
            )

        with patch("msg2md.os.fdopen", side_effect=failing_fdopen):
            with self.assertRaises(OSError):
                convert_message(source)

        self.assertFalse(destination.exists())
        self.assertEqual(source.read_bytes(), original_bytes)


    @patch("msg2md.extract_msg.Message")
    def test_named_attachment_is_listed(self, mock_message_class):
        source = self.make_source()

        message = self.mock_message()
        attachment = MagicMock()
        attachment.longFilename = "project-plan.pdf"
        attachment.shortFilename = "PROJECT~1.PDF"
        message.attachments = [attachment]

        mock_message_class.return_value = message

        destination = convert_message(source)
        content = destination.read_text(encoding="utf-8")

        self.assertIn("## Attachments", content)
        self.assertIn("project-plan.pdf", content)
        self.assertNotIn("PROJECT~1.PDF", content)

        # Conversion must not save attachment contents.
        attachment.save.assert_not_called()

        # No attachment files should be created.
        self.assertEqual(
            sorted(p.name for p in self.directory.iterdir()),
            ["test.md", "test.msg"],
        )


    @patch("msg2md.extract_msg.Message")
    def test_no_attachments(self, mock_message_class):
        source = self.make_source()

        message = self.mock_message()
        message.attachments = []
        mock_message_class.return_value = message

        destination = convert_message(source)
        content = destination.read_text(encoding="utf-8")

        self.assertIn("## Attachments", content)
        self.assertIn("## Attachments\n\nNone", content)

    @patch("msg2md.extract_msg.Message")
    def test_unnamed_attachment(self, mock_message_class):
        source = self.make_source()

        message = self.mock_message()
        attachment = MagicMock()
        attachment.longFilename = None
        attachment.shortFilename = None
        message.attachments = [attachment]

        mock_message_class.return_value = message

        destination = convert_message(source)
        content = destination.read_text(encoding="utf-8")

        self.assertIn("- Unnamed attachment", content)
        attachment.save.assert_not_called()


    @patch("msg2md.extract_msg.Message")
    def test_html_only_message(self, mock_message_class):
        source = self.make_source()

        message = self.mock_message(body=None)
        message.htmlBody = (
            b"<html><body>"
            b"<p>Hello Bob,</p>"
            b"<p>Please review the "
            b'<a href="https://example.com">project page</a>.'
            b"</p>"
            b"<ul><li>First item</li><li>Second item</li></ul>"
            b"<p>Regards,<br>Alice</p>"
            b"</body></html>"
        )
        message.attachments = []

        mock_message_class.return_value = message

        destination = convert_message(source)
        content = destination.read_text(encoding="utf-8")

        self.assertIn("## Body", content)
        self.assertIn("Hello Bob,", content)
        self.assertIn(
            "[project page](https://example.com)",
            content,
        )
        self.assertIn("First item", content)
        self.assertIn("Second item", content)
        self.assertIn("Regards,", content)
        self.assertIn("Alice", content)


    @patch("msg2md.extract_msg.Message")
    def test_plain_text_preferred_over_html(
        self, mock_message_class
    ):
        source = self.make_source()

        message = self.mock_message(
            body="Original plain-text message.",
            htmlBody=(
                b"<html><body>"
                b"<p>Different HTML message.</p>"
                b"</body></html>"
            ),
        )

        mock_message_class.return_value = message

        destination = convert_message(source)
        content = destination.read_text(encoding="utf-8")

        self.assertIn(
            "Original plain-text message.",
            content,
        )
        self.assertNotIn(
            "Different HTML message.",
            content,
        )


    @patch("msg2md.extract_msg.Message")
    def test_html_without_readable_content_fails(
        self, mock_message_class
    ):
        source = self.make_source()

        message = self.mock_message(
            body=None,
            htmlBody=b"<html><body><div></div></body></html>",
        )

        mock_message_class.return_value = message

        with self.assertRaises(ValueError):
            convert_message(source)

        self.assertFalse(source.with_suffix(".md").exists())


    @patch("msg2md.extract_msg.Message")
    def test_html_windows_1252_encoding(
        self, mock_message_class
    ):
        source = self.make_source()

        html = (
            '<html><head>'
            '<meta charset="windows-1252">'
            '</head><body>'
            '<p>Café résumé — €100</p>'
            '</body></html>'
        ).encode("cp1252")

        message = self.mock_message(
            body=None,
            htmlBody=html,
        )

        mock_message_class.return_value = message

        destination = convert_message(source)
        content = destination.read_text(encoding="utf-8")

        self.assertIn("Café résumé — €100", content)


    @patch("msg2md.extract_msg.Message")
    def test_html_excludes_scripts_and_styles(
        self, mock_message_class
    ):
        source = self.make_source()

        html = (
            b"<html><head>"
            b"<style>SECRET_STYLE_MARKER</style>"
            b"<script>SECRET_SCRIPT_MARKER</script>"
            b"</head><body>"
            b"<p>This is the actual email message.</p>"
            b"</body></html>"
        )

        message = self.mock_message(
            body=None,
            htmlBody=html,
        )
        mock_message_class.return_value = message

        destination = convert_message(source)
        content = destination.read_text(encoding="utf-8")

        self.assertIn(
            "This is the actual email message.",
            content,
        )
        self.assertNotIn("SECRET_STYLE_MARKER", content)
        self.assertNotIn("SECRET_SCRIPT_MARKER", content)


    @patch("msg2md.extract_msg.Message")
    def test_metadata_markdown_escaping(
        self, mock_message_class
    ):
        source = self.make_source()

        message = self.mock_message(
            subject="Project *Alpha* [Review]",
        )
        mock_message_class.return_value = message

        destination = convert_message(source)
        content = destination.read_text(encoding="utf-8")

        self.assertIn(
            r"**Subject:** Project \*Alpha\* \[Review\]",
            content,
        )


    @patch("msg2md.extract_msg.Message")
    def test_metadata_newlines_are_safe(
        self, mock_message_class
    ):
        source = self.make_source()

        message = self.mock_message(
            subject="Project Update\n# Important",
        )
        mock_message_class.return_value = message

        destination = convert_message(source)
        content = destination.read_text(encoding="utf-8")

        self.assertIn(
            "**Subject:** Project Update # Important",
            content,
        )
        self.assertNotIn(
            "\\n# Important",
            content,
        )


    @patch("msg2md.extract_msg.Message")
    def test_corrupted_msg_does_not_create_output(
        self, mock_message_class
    ):
        source = self.make_source()
        original_bytes = source.read_bytes()

        mock_message_class.side_effect = ValueError(
            "Invalid Outlook MSG structure"
        )

        with self.assertRaises(ValueError):
            convert_message(source)

        self.assertFalse(source.with_suffix(".md").exists())
        self.assertEqual(source.read_bytes(), original_bytes)


    @patch("msg2md.convert_message")
    def test_cli_hides_unexpected_error_details(
        self, mock_convert
    ):
        import io
        from contextlib import redirect_stdout

        from msg2md import main

        mock_convert.side_effect = RuntimeError(
            "Confidential email content"
        )

        output = io.StringIO()

        with patch(
            "sys.argv",
            ["msg2md.py", "test.msg"],
        ):
            with redirect_stdout(output):
                exit_code = main()

        self.assertNotEqual(exit_code, 0)
        self.assertIn("Error:", output.getvalue())
        self.assertNotIn(
            "Confidential email content",
            output.getvalue(),
        )


    @patch("msg2md.extract_msg.Message")
    def test_plain_text_body_fidelity(
        self, mock_message_class
    ):
        source = self.make_source()
        original_bytes = source.read_bytes()

        original_body = (
            "Hello Bob,\\n"
            "\\n"
            "Please review the résumé for José.\\n"
            "The estimated cost is €250.\\n"
            "\\n"
            "# Project Update\\n"
            "*Important*\\n"
            "- Action item\\n"
            "\\n"
            "Regards,\\n"
            "Alice\\n"
            "\\n"
            "-----Original Message-----\\n"
            "From: Bob\\n"
            "Sent: Monday\\n"
            "> Previous message line 1\\n"
            "> Previous message line 2"
        )

        message = self.mock_message(
            body=original_body,
            htmlBody=None,
        )
        mock_message_class.return_value = message

        destination = convert_message(source)
        content = destination.read_text(encoding="utf-8")

        # The complete original body must appear unchanged.
        self.assertIn(original_body, content)

        # Verify important preservation cases.
        self.assertIn("résumé for José", content)
        self.assertIn("€250", content)
        self.assertIn("Regards,\\nAlice", content)
        self.assertIn("-----Original Message-----", content)
        self.assertIn("> Previous message line 1", content)
        self.assertIn("# Project Update", content)
        self.assertIn("*Important*", content)

        # The original MSG must remain unchanged.
        self.assertEqual(source.read_bytes(), original_bytes)


if __name__ == "__main__":
    unittest.main()
