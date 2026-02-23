import re
from analyzers import (
    check_contact_info,
    check_sections,
    check_work_experience,
    check_education,
    check_formatting,
    check_ats_compatibility,
    check_action_verbs,
    check_measurable_results,
    check_hard_skills,
    check_readability,
    check_consistency,
    check_keyword_optimization,
)
from tips import generate_tips


def _resume_confidence(text, text_lower):
    """Score 0-1 indicating how likely this document is actually a resume."""
    signals = 0
    max_signals = 10

    has_email = bool(re.search(r"[\w.+-]+\s*@\s*[\w-]+\s*\.\s*[\w.]+", text))
    has_phone = bool(re.search(r"(?:\+?\d[\d\s\-().]{7,}\d)", text))
    if has_email:
        signals += 1.5
    if has_phone:
        signals += 1.5

    resume_headings = ["work experience", "professional experience", "education",
                       "skills", "technical skills", "summary", "objective",
                       "certifications", "projects"]
    lines = text_lower.split("\n")
    heading_count = 0
    for line in lines:
        stripped = line.strip().rstrip(":").strip()
        if stripped and len(stripped) < 50:
            for h in resume_headings:
                if h in stripped:
                    heading_count += 1
                    break
    if heading_count >= 3:
        signals += 3
    elif heading_count >= 2:
        signals += 2
    elif heading_count >= 1:
        signals += 1

    date_ranges = re.findall(
        r"(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)\w*\.?\s*\d{4}\s*[–\-—to]+",
        text_lower)
    year_ranges = re.findall(r"\b20\d{2}\s*[–\-—]\s*(?:20\d{2}|present|current)\b", text_lower)
    if len(date_ranges) + len(year_ranges) >= 2:
        signals += 2
    elif len(date_ranges) + len(year_ranges) >= 1:
        signals += 1

    bullet_chars = ["•", "●", "▪", "■", "–", "→", "◦", "‣", "►"]
    bullet_lines = sum(1 for l in lines if any(l.strip().startswith(c) for c in bullet_chars))
    if bullet_lines >= 5:
        signals += 2
    elif bullet_lines >= 2:
        signals += 1

    return min(signals / max_signals, 1.0)


def analyze_resume(text, num_pages, file_ext):
    text_lower = text.lower()

    confidence = _resume_confidence(text, text_lower)

    checks = [
        ("Contact Information", lambda: check_contact_info(text, text_lower)),
        ("Resume Sections", lambda: check_sections(text_lower)),
        ("Work Experience", lambda: check_work_experience(text, text_lower)),
        ("Education", lambda: check_education(text, text_lower)),
        ("Formatting & Structure", lambda: check_formatting(text, num_pages)),
        ("ATS Compatibility", lambda: check_ats_compatibility(text, file_ext)),
        ("Action Verbs", lambda: check_action_verbs(text_lower)),
        ("Measurable Results", lambda: check_measurable_results(text, text_lower)),
        ("Hard Skills", lambda: check_hard_skills(text_lower)),
        ("Readability", lambda: check_readability(text)),
        ("Writing Consistency", lambda: check_consistency(text)),
        ("Keyword Optimization", lambda: check_keyword_optimization(text_lower)),
    ]

    total_score = 0
    total_max = 0
    categories = []

    for name, fn in checks:
        s, m, findings = fn()
        total_score += s
        total_max += m
        pct = round((s / m) * 100) if m else 0
        categories.append({
            "name": name,
            "score": round(s, 1),
            "max_score": m,
            "percentage": pct,
            "findings": findings,
        })

    raw_overall = round((total_score / total_max) * 100) if total_max else 0

    if confidence < 0.3:
        overall = round(raw_overall * 0.4)
    elif confidence < 0.5:
        overall = round(raw_overall * 0.65)
    elif confidence < 0.7:
        overall = round(raw_overall * 0.85)
    else:
        overall = raw_overall

    if confidence < 0.3:
        for cat in categories:
            cat["percentage"] = round(cat["percentage"] * 0.4)
    elif confidence < 0.5:
        for cat in categories:
            cat["percentage"] = round(cat["percentage"] * 0.65)
    elif confidence < 0.7:
        for cat in categories:
            cat["percentage"] = round(cat["percentage"] * 0.85)

    if confidence < 0.3:
        verdict = "This document doesn't appear to be a resume. Please upload a proper resume with sections like Experience, Education, Skills, and contact information."
    elif confidence < 0.5:
        verdict = "This document has very few resume characteristics. Make sure it has proper section headings, contact info, dates, and bullet points."
    elif overall >= 85:
        verdict = "Excellent! Your resume is highly optimized for ATS systems. Fine-tune with the tips below to reach perfection."
    elif overall >= 70:
        verdict = "Good resume! You're above average, but several improvements could significantly boost your ATS pass rate."
    elif overall >= 55:
        verdict = "Decent foundation, but needs work. Follow the priority tips below to improve your chances significantly."
    elif overall >= 40:
        verdict = "Below average ATS compatibility. Multiple critical areas need attention — focus on the high-priority tips first."
    else:
        verdict = "Significant improvements needed. Your resume will likely be filtered out by most ATS systems. Start with the top recommendations."

    tips = generate_tips(categories, overall, text_lower)

    total_findings = sum(len(c["findings"]) for c in categories)
    pass_count = sum(1 for c in categories for f in c["findings"] if f["type"] == "pass")
    fail_count = sum(1 for c in categories for f in c["findings"] if f["type"] == "fail")
    warn_count = sum(1 for c in categories for f in c["findings"] if f["type"] == "warning")

    return {
        "overall_score": overall,
        "verdict": verdict,
        "categories": categories,
        "tips": tips,
        "summary_stats": {
            "total_checks": total_findings,
            "passed": pass_count,
            "warnings": warn_count,
            "failed": fail_count,
        },
        "score_breakdown": {
            "total_earned": round(total_score, 1),
            "total_possible": total_max,
        }
    }
