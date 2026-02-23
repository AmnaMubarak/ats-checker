import re
from constants import UNPROFESSIONAL_EMAIL_WORDS


def check_contact_info(text, text_lower):
    findings = []
    score = 0
    max_score = 12

    text_collapsed = re.sub(r"\s+", " ", text)
    text_no_spaces = re.sub(r"\s+", "", text_lower)

    email_match = re.search(r"[a-zA-Z0-9._%+\-]+\s*@\s*[a-zA-Z0-9.\-]+\.\s*[a-zA-Z]{2,}", text)
    if not email_match:
        email_match = re.search(r"[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}", text_collapsed)

    phone_match = re.search(r"[\+]?[\d\s\-\(\)]{7,15}", text)

    linkedin_match = (
        re.search(r"linkedin\.com/in/[\w\-]+", text, re.IGNORECASE) or
        re.search(r"linkedin\s*\.\s*com\s*/\s*in\s*/\s*[\w\-]+", text, re.IGNORECASE) or
        re.search(r"linkedin\.com/in/[\w\-]+", text_collapsed, re.IGNORECASE) or
        re.search(r"linkedin\.?com/?in/?[\w\-]+", text_no_spaces) or
        re.search(r"\blinkedin\b", text_lower)
    )
    linkedin_is_keyword_only = (
        not re.search(r"linkedin\.com/in/[\w\-]+", text_collapsed, re.IGNORECASE)
        and re.search(r"\blinkedin\b", text_lower)
    )

    github_match = (
        re.search(r"github\.com/[\w\-]+", text, re.IGNORECASE) or
        re.search(r"github\s*\.\s*com\s*/\s*[\w\-]+", text, re.IGNORECASE) or
        re.search(r"github\.com/[\w\-]+", text_collapsed, re.IGNORECASE) or
        re.search(r"github\.?com/?[\w\-]+", text_no_spaces) or
        re.search(r"\bgithub\b", text_lower)
    )
    github_is_keyword_only = (
        not re.search(r"github\.com/[\w\-]+", text_collapsed, re.IGNORECASE)
        and re.search(r"\bgithub\b", text_lower)
    )

    website_match = (
        re.search(r"(?:portfolio|website|http|www\.)\S+", text, re.IGNORECASE) or
        re.search(r"(?:portfolio|website|http|www\.)\S+", text_collapsed, re.IGNORECASE) or
        re.search(r"\b(?:portfolio|website)\b", text_lower)
    )

    location_match = (
        re.search(r"\b(?:city|state|country|zip|located in|based in|remote|hybrid)\b", text_lower) or
        re.search(r"\b[A-Z][a-z]+,\s*[A-Z]{2}\b", text) or
        re.search(r"\b[A-Z][a-z]+,\s*[A-Z][a-z]+\b", text)
    )

    if email_match:
        score += 3
        email_addr = re.sub(r"\s+", "", email_match.group()).lower()
        domain = email_addr.split("@")[1] if "@" in email_addr else ""
        local = email_addr.split("@")[0] if "@" in email_addr else ""

        if any(w in local for w in UNPROFESSIONAL_EMAIL_WORDS):
            findings.append({"type": "warning", "message": f"Email found ({email_addr}) but may seem unprofessional — use firstname.lastname format"})
        elif domain in ("gmail.com", "outlook.com", "yahoo.com", "hotmail.com", "protonmail.com"):
            findings.append({"type": "pass", "message": f"Professional email found: {email_addr}"})
        else:
            findings.append({"type": "pass", "message": f"Email address found: {email_addr}"})
    else:
        findings.append({"type": "fail", "message": "No email address found — this is critical for ATS systems to contact you"})

    if phone_match:
        score += 3
        findings.append({"type": "pass", "message": "Phone number detected"})
    else:
        findings.append({"type": "fail", "message": "No phone number found — recruiters need a way to call you"})

    if linkedin_match:
        score += 2
        if linkedin_is_keyword_only:
            findings.append({"type": "pass", "message": "LinkedIn reference found (URL may be hyperlinked in original — PDF extraction can break links)"})
        else:
            findings.append({"type": "pass", "message": "LinkedIn profile URL detected"})
    else:
        findings.append({"type": "warning", "message": "No LinkedIn URL — 87% of recruiters use LinkedIn; add your profile link"})

    if github_match:
        score += 2
        if github_is_keyword_only:
            findings.append({"type": "pass", "message": "GitHub reference found (URL may be hyperlinked in original — PDF extraction can break links)"})
        else:
            findings.append({"type": "pass", "message": "GitHub profile URL detected"})
    elif website_match:
        score += 2
        findings.append({"type": "pass", "message": "Portfolio/Website link detected"})
    else:
        findings.append({"type": "info", "message": "No portfolio/GitHub link — consider adding one to stand out"})

    if location_match:
        score += 2
        findings.append({"type": "pass", "message": "Location information detected"})
    else:
        findings.append({"type": "warning", "message": "No location detected — some employers filter by location, add city/state or 'Remote'"})

    return round(min(score, max_score), 1), max_score, findings
