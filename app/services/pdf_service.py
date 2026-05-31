"""
PDF service — text extraction and file validation.

Single source of truth for PDF operations, replacing the duplicated
extraction logic that was in both main.py and question_processor.py.
"""

import os
import PyPDF2


ALLOWED_EXTENSIONS = {'pdf'}


def allowed_file(filename):
    """Check if a filename has an allowed extension."""
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def extract_text(filepath):
    """Extract all text from a PDF file.

    Args:
        filepath: Absolute path to the PDF file.

    Returns:
        The concatenated text from all pages, or empty string on error.
    """
    text = ""
    try:
        with open(filepath, 'rb') as f:
            reader = PyPDF2.PdfReader(f)
            for page in reader.pages:
                extracted = page.extract_text()
                if extracted:
                    text += extracted + "\n"
    except Exception as e:
        print(f"Error extracting PDF text: {e}")
    return text


def generate_unique_filename(upload_folder, filename):
    """Return a filename that doesn't collide with existing files.

    If 'report.pdf' exists, returns 'report_1.pdf', 'report_2.pdf', etc.
    """
    filepath = os.path.join(upload_folder, filename)
    if not os.path.exists(filepath):
        return filename

    base, extension = os.path.splitext(filename)
    i = 1
    while os.path.exists(os.path.join(upload_folder, f"{base}_{i}{extension}")):
        i += 1
    return f"{base}_{i}{extension}"
