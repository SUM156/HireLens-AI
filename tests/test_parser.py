"""
Tests for parser.py — file reading, format detection, and error handling.
All tests use temporary files so nothing touches real resume data.
"""

import unittest
import tempfile
from pathlib import Path

from src.parser import parse_resume, parse_txt, ParseError


class TestParseTxt(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.TemporaryDirectory()
        self.dir = Path(self.tmpdir.name)

    def tearDown(self):
        self.tmpdir.cleanup()

    def test_parse_txt_valid_file(self):
        # Normal UTF-8 text file should parse cleanly.
        f = self.dir / "resume.txt"
        f.write_text("Sumair Ahmed\nPython Developer\nExperience: 2 years", encoding="utf-8")
        result = parse_txt(str(f))
        self.assertIn("Sumair Ahmed", result)

    def test_parse_txt_missing_file_raises(self):
        with self.assertRaises(ParseError):
            parse_txt(str(self.dir / "missing.txt"))


class TestParseResume(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.TemporaryDirectory()
        self.dir = Path(self.tmpdir.name)

    def tearDown(self):
        self.tmpdir.cleanup()

    def test_dispatches_txt(self):
        # parse_resume should call parse_txt for .txt files.
        f = self.dir / "resume.txt"
        content = "John Doe\nSoftware Engineer\n" + "Python developer with experience " * 5
        f.write_text(content, encoding="utf-8")
        result = parse_resume(str(f))
        self.assertIn("John Doe", result)

    def test_unsupported_extension_raises(self):
        f = self.dir / "resume.docx"
        f.write_bytes(b"fake docx content that is long enough to not trigger length check")
        with self.assertRaises(ParseError):
            parse_resume(str(f))

    def test_too_short_content_raises(self):
        # Files with < 50 chars of content should be rejected as unanalyzable.
        f = self.dir / "tiny.txt"
        f.write_text("Hi", encoding="utf-8")
        with self.assertRaises(ParseError):
            parse_resume(str(f))

    def test_trailing_whitespace_stripped(self):
        f = self.dir / "resume.txt"
        content = "  Sumair Ahmed   \n  Python Developer  \n" + "x " * 30
        f.write_text(content, encoding="utf-8")
        result = parse_resume(str(f))
        # Leading/trailing whitespace per line should be stripped
        self.assertFalse(result.startswith(" "))
        self.assertFalse(result.endswith(" "))


if __name__ == "__main__":
    unittest.main()