import re
from constants import ATS_UNFRIENDLY_CHARS


def check_ats_compatibility(text, file_ext):
    findings = []
    score = 0
    max_score = 8

    if file_ext == "pdf":
        score += 2
        findings.append({"type": "pass", "message": "PDF format — universally accepted by ATS systems"})
    elif file_ext == "docx":
        score += 2
        findings.append({"type": "pass", "message": "DOCX format — excellent ATS compatibility (preferred by many systems)"})

    special_chars = [c for c in ATS_UNFRIENDLY_CHARS if c in text]
    if not special_chars:
        score += 2
        findings.append({"type": "pass", "message": "No problematic special characters — clean text for ATS parsing"})
    elif len(special_chars) <= 3:
        score += 1
        findings.append({"type": "warning", "message": "Some special characters found that may not parse correctly in all ATS systems"})
    else:
        findings.append({"type": "fail", "message": "Multiple special characters detected — replace symbols with standard text equivalents"})

    header_footer_keywords = ["page 1", "page 2", "page 3", "header", "footer",
                               "confidential", "curriculum vitae"]
    found_hf = [kw for kw in header_footer_keywords if kw in text.lower()]
    if not found_hf:
        score += 1.5
        findings.append({"type": "pass", "message": "No headers/footers detected — ATS often misreads content in headers/footers"})
    else:
        score += 0.5
        findings.append({"type": "warning", "message": "Possible header/footer content — some ATS systems skip header/footer areas"})

    table_indicators = re.findall(r"\t{2,}|\s{4,}\S+\s{4,}\S+", text)
    if len(table_indicators) > 5:
        findings.append({"type": "warning", "message": "Possible table/column layout detected — ATS may scramble multi-column layouts; use single-column format"})
    else:
        score += 1.5
        findings.append({"type": "pass", "message": "Layout appears ATS-friendly — no complex table structures detected"})

    image_indicators = re.findall(r"\[image\]|\[photo\]|\[logo\]|\.(?:png|jpg|jpeg|gif|svg)\b", text, re.IGNORECASE)
    if image_indicators:
        findings.append({"type": "warning", "message": "Image references detected — ATS cannot read images; ensure all info is in text form"})
    else:
        score += 1
        findings.append({"type": "pass", "message": "No image-only content detected — all content is text-based and parseable"})

    return round(min(score, max_score), 1), max_score, findings
