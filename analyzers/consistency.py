import re


def check_consistency(text):
    findings = []
    score = 0
    max_score = 7

    past_tense = len(re.findall(r"\b\w+ed\b", text))
    present_tense = len(re.findall(r"\b(?:manage|develop|lead|create|design|implement|build|maintain|coordinate|optimize|analyze|deliver|support|organize)\b", text, re.IGNORECASE))

    if past_tense > 0 and present_tense > 0:
        ratio = min(past_tense, present_tense) / max(past_tense, present_tense)
        if ratio > 0.6:
            score += 1
            findings.append({"type": "warning", "message": f"Mixed verb tenses (past: ~{past_tense}, present: ~{present_tense}) — use past tense for previous roles, present for current"})
        else:
            score += 2.5
            dominant = "past" if past_tense > present_tense else "present"
            findings.append({"type": "pass", "message": f"Consistent verb tense — primarily {dominant} tense with appropriate variation"})
    elif past_tense > 0:
        score += 2.5
        findings.append({"type": "pass", "message": "Consistent use of past tense — appropriate for describing completed work"})
    elif present_tense > 0:
        score += 2
        findings.append({"type": "pass", "message": "Present tense usage — appropriate for current role"})
    else:
        score += 1
        findings.append({"type": "info", "message": "Could not determine verb tense pattern"})

    first_person = re.findall(r"\b(?:I|my|me|myself)\b", text)
    if len(first_person) == 0:
        score += 2.5
        findings.append({"type": "pass", "message": "No first-person pronouns — correct resume writing style"})
    elif len(first_person) <= 3:
        score += 1.5
        findings.append({"type": "warning", "message": f"Found {len(first_person)} first-person pronoun(s) (I/my/me) — resumes should omit these"})
    else:
        findings.append({"type": "fail", "message": f"{len(first_person)} first-person pronouns found — remove all 'I', 'my', 'me' from your resume"})

    mixed_abbrev = []
    abbrev_pairs = [("JavaScript", "JS"), ("TypeScript", "TS"), ("Structured Query Language", "SQL"),
                    ("Application", "App"), ("Development", "Dev"), ("Management", "Mgmt")]
    text_lower = text.lower()
    for full, short in abbrev_pairs:
        if full.lower() in text_lower and short.lower() in text_lower:
            mixed_abbrev.append(f"{full}/{short}")

    if not mixed_abbrev:
        score += 2
        findings.append({"type": "pass", "message": "Consistent terminology — no mixed abbreviations detected"})
    else:
        score += 1
        findings.append({"type": "warning", "message": f"Mixed abbreviations: {', '.join(mixed_abbrev)} — pick one form and use it consistently"})

    return round(min(score, max_score), 1), max_score, findings
