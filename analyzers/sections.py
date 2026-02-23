from constants import SECTION_KEYWORDS


def _find_section_heading(text_lower, keywords):
    """Check if a keyword appears as a section heading (on its own line or near the start of a line)."""
    lines = text_lower.split("\n")
    for line in lines:
        stripped = line.strip().rstrip(":").strip()
        if not stripped:
            continue
        for kw in keywords:
            if stripped == kw:
                return True
            if stripped.startswith(kw) and len(stripped) < len(kw) + 15:
                return True
            if kw in stripped and len(stripped) < 50:
                return True
    return False


def check_sections(text_lower):
    findings = []
    score = 0
    max_score = 15

    critical = {"experience": 4, "education": 4, "skills": 4}
    important = {"summary": 1.5}
    nice_to_have = {"certifications": 0.5, "projects": 0.5, "awards": 0.3,
                    "languages": 0.3, "volunteer": 0.2}

    found_sections = []

    for section, pts in critical.items():
        found = _find_section_heading(text_lower, SECTION_KEYWORDS[section])
        if found:
            score += pts
            found_sections.append(section.title())
            findings.append({"type": "pass", "message": f"'{section.title()}' section found"})
        else:
            findings.append({"type": "fail", "message": f"Missing '{section.title()}' section — this is essential for ATS parsing"})

    for section, pts in important.items():
        found = _find_section_heading(text_lower, SECTION_KEYWORDS[section])
        if found:
            score += pts
            found_sections.append(section.title())
            findings.append({"type": "pass", "message": f"'{section.title()}' section found — helps recruiters quickly assess your profile"})
        else:
            findings.append({"type": "warning", "message": f"No '{section.title()}' section — a strong summary can boost recruiter interest by 36%"})

    nice_found = 0
    for section, pts in nice_to_have.items():
        found = _find_section_heading(text_lower, SECTION_KEYWORDS[section])
        if found:
            score += pts
            nice_found += 1
            found_sections.append(section.title())

    if nice_found > 0:
        names = [s for s in ["Certifications", "Projects", "Awards", "Languages", "Volunteer"]
                 if s in found_sections]
        findings.append({"type": "pass", "message": f"Bonus sections found: {', '.join(names)}"})
    else:
        findings.append({"type": "info", "message": "Consider adding: Certifications, Projects, Awards, or Languages to strengthen your resume"})

    findings.append({"type": "info", "message": f"Total sections detected: {len(found_sections)} ({', '.join(found_sections)})"})

    return round(min(score, max_score), 1), max_score, findings
