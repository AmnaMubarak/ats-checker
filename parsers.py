from PyPDF2 import PdfReader
from docx import Document
from config import ALLOWED_EXTENSIONS


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def extract_text_from_pdf(filepath):
    text = ""
    reader = PdfReader(filepath)
    num_pages = len(reader.pages)
    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            text += page_text + "\n"
    return text, num_pages


def extract_text_from_docx(filepath):
    doc = Document(filepath)
    text = "\n".join(p.text for p in doc.paragraphs)
    page_estimate = max(1, len(text.split()) // 450)
    return text, page_estimate


def extract_text(filepath):
    ext = filepath.rsplit(".", 1)[1].lower()
    if ext == "pdf":
        return extract_text_from_pdf(filepath)
    elif ext == "docx":
        return extract_text_from_docx(filepath)
    return "", 0
