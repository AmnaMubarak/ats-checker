import re


def check_formatting(text, num_pages):
    findings = []
    score = 0
    max_score = 13

    words = text.split()
    word_count = len(words)
    lines = text.strip().split("\n")
    non_empty_lines = [l for l in lines if l.strip()]

    if num_pages == 1:
        score += 2
        findings.append({"type": "pass", "message": "Single-page resume — ideal for most positions"})
    elif num_pages == 2:
        score += 2
        findings.append({"type": "pass", "message": "Two-page resume — acceptable for experienced professionals"})
    elif num_pages >= 3:
        score += 0.5
        findings.append({"type": "warning", "message": f"{num_pages}-page resume detected — keep it to 1–2 pages unless you have 10+ years of experience"})

    if 400 <= word_count <= 800:
        score += 2
        findings.append({"type": "pass", "message": f"Optimal word count: {word_count} words (ideal range: 400–800)"})
    elif 300 <= word_count < 400:
        score += 1.5
        findings.append({"type": "warning", "message": f"Slightly short ({word_count} words) — aim for 400–800 words to provide enough detail"})
    elif 800 < word_count <= 1100:
        score += 1.5
        findings.append({"type": "warning", "message": f"Slightly long ({word_count} words) — consider trimming less relevant details"})
    elif word_count < 300:
        score += 0.5
        findings.append({"type": "fail", "message": f"Too short ({word_count} words) — your resume needs more content to be competitive"})
    else:
        score += 0.5
        findings.append({"type": "fail", "message": f"Too long ({word_count} words) — recruiters spend 7 seconds on initial scan, be concise"})

    bullet_chars = ["•", "●", "▪", "■", "-", "–", "→", "*", "◦", "‣", "►"]
    bullet_lines = sum(1 for l in non_empty_lines if any(l.strip().startswith(c) for c in bullet_chars))
    bullet_ratio = bullet_lines / max(len(non_empty_lines), 1)

    if bullet_ratio > 0.2:
        score += 3
        findings.append({"type": "pass", "message": f"Excellent bullet point usage ({bullet_lines} bullet lines, {round(bullet_ratio * 100)}% of content)"})
    elif bullet_ratio > 0.1:
        score += 2
        findings.append({"type": "pass", "message": f"Good bullet usage ({bullet_lines} bullets) — could add a few more for readability"})
    elif bullet_ratio > 0.03:
        score += 1
        findings.append({"type": "warning", "message": f"Limited bullet points ({bullet_lines} found) — restructure experience as bullet points for better ATS parsing"})
    else:
        findings.append({"type": "fail", "message": "Almost no bullet points — ATS systems and recruiters strongly prefer bulleted experience"})

    year_dates = re.findall(r"\b(20\d{2}|19\d{2})\b", text)
    month_names = re.findall(r"\b(jan(?:uary)?|feb(?:ruary)?|mar(?:ch)?|apr(?:il)?|may|jun(?:e)?|jul(?:y)?|aug(?:ust)?|sep(?:tember)?|oct(?:ober)?|nov(?:ember)?|dec(?:ember)?)\b", text, re.IGNORECASE)
    date_ranges = re.findall(r"(?:present|current|ongoing)", text, re.IGNORECASE)

    if year_dates and month_names:
        score += 3
        findings.append({"type": "pass", "message": f"Proper date formatting ({len(year_dates)} years, {len(month_names)} months detected)"})
        if date_ranges:
            findings.append({"type": "pass", "message": "Current position indicated with 'Present' — ATS can parse employment timeline"})
    elif year_dates:
        score += 2
        findings.append({"type": "warning", "message": f"Year dates found ({len(year_dates)}) but no month names — use 'Jan 2023 – Present' format for best ATS parsing"})
    else:
        findings.append({"type": "fail", "message": "No date information detected — add employment and education dates (e.g., 'Sep 2021 – Jun 2024')"})

    long_lines = sum(1 for l in non_empty_lines if len(l.strip()) > 120)
    if long_lines > len(non_empty_lines) * 0.3:
        score += 0.5
        findings.append({"type": "warning", "message": f"{long_lines} very long lines detected — break up dense paragraphs into shorter bullet points"})
    else:
        score += 1.5
        findings.append({"type": "pass", "message": "Content has good line-length distribution — readable for both ATS and humans"})

    caps_lines = sum(1 for l in non_empty_lines if l.strip().isupper() and len(l.strip()) > 3)
    if caps_lines > 6:
        findings.append({"type": "warning", "message": f"Excessive ALL CAPS text ({caps_lines} lines) — use title case for headings instead"})
    elif caps_lines > 0:
        score += 0.5
        findings.append({"type": "pass", "message": "Appropriate use of capitalization for section headings"})

    return round(min(score, max_score), 1), max_score, findings
