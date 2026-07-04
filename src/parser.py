"""
parser.py
----------
Extracts clean, readable text from a resume file.

Supported formats: PDF (.pdf) and plain text (.txt)

WHY SEPARATE PARSING FROM ANALYSIS?
The AI analyzer (analyzer.py) should receive clean text — it should not
know or care whether the original file was a PDF or a .txt file. This
separation means:
  1. Adding a new format (e.g. .docx) later only requires changing this
     file — the AI layer stays untouched.
  2. Text extraction can be unit-tested without making any AI API calls.
  3. If the PDF parser library changes, only this file needs updating.

WHY pypdf for PDF extraction?
pypdf is a pure-Python, dependency-light PDF text extractor. For resume
PDFs (which are typically simple, text-based documents — not scanned
images), it handles extraction reliably. For scanned/image PDFs, you
would need OCR (e.g. pytesseract), but that is outside the scope of this
version and noted in the README roadmap.
"""

from pathlib import Path

try:
    # pypdf is the modern successor to PyPDF2
    from pypdf import PdfReader
    _PYPDF_AVAILABLE = True
except ImportError:
    _PYPDF_AVAILABLE = False


class ParseError(Exception):
    """Raised when a resume file cannot be read or parsed."""
    pass


def parse_pdf(filepath: str) -> str:
    """
    Extract all text from a PDF file and return it as a single string.

    We iterate over every page and join their text with newlines so that
    section boundaries between pages are preserved in the output.

    Args:
        filepath: absolute or relative path to the PDF file.

    Returns:
        A single string containing all extracted text.

    Raises:
        ParseError if pypdf is not installed or the file cannot be read.
    """
    if not _PYPDF_AVAILABLE:
        raise ParseError(
            "pypdf is not installed. Run: pip install pypdf"
        )

    path = Path(filepath)
    if not path.exists():
        raise ParseError(f"File not found: {filepath}")

    try:
        reader = PdfReader(str(path))
    except Exception as exc:
        raise ParseError(f"Could not open PDF '{filepath}': {exc}") from exc

    # Extract text from each page and join with double newlines to preserve
    # the visual separation between pages.
    pages_text = []
    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:  # some pages may be blank or image-only
            pages_text.append(page_text.strip())

    if not pages_text:
        raise ParseError(
            "No text could be extracted from the PDF. "
            "The file may be scanned/image-based and requires OCR."
        )

    return "\n\n".join(pages_text)


def parse_txt(filepath: str) -> str:
    """
    Read a plain-text resume file and return its content.

    Args:
        filepath: path to the .txt file.

    Returns:
        File content as a string.

    Raises:
        ParseError if the file is missing or cannot be decoded as UTF-8.
    """
    path = Path(filepath)
    if not path.exists():
        raise ParseError(f"File not found: {filepath}")

    try:
        # We try UTF-8 first (modern standard), then fall back to latin-1
        # which can read almost any byte sequence without crashing.
        try:
            return path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            return path.read_text(encoding="latin-1")
    except OSError as exc:
        raise ParseError(f"Could not read file '{filepath}': {exc}") from exc


def parse_resume(filepath: str) -> str:
    """
    Auto-detect the file type from the extension and extract text.

    This is the single entry point that the rest of the codebase uses —
    callers don't need to know whether the file is a PDF or TXT.

    Args:
        filepath: path to a .pdf or .txt resume file.

    Returns:
        Extracted text, stripped of leading/trailing whitespace.

    Raises:
        ParseError for unsupported extensions or failed extraction.
    """
    ext = Path(filepath).suffix.lower()

    if ext == ".pdf":
        text = parse_pdf(filepath)
    elif ext == ".txt":
        text = parse_txt(filepath)
    else:
        raise ParseError(
            f"Unsupported file type '{ext}'. "
            "ResumeIQ supports .pdf and .txt files."
        )

    # Strip excessive whitespace that PDF extractors often leave behind
    # (multiple consecutive blank lines, trailing spaces per line, etc.)
    lines = [line.rstrip() for line in text.splitlines()]
    cleaned = "\n".join(lines).strip()

    if len(cleaned) < 50:
        raise ParseError(
            "The extracted resume text is too short to analyze. "
            "Please check that the file contains readable text."
        )

    return cleaned