import re
from constants import ACTION_VERBS_BY_CATEGORY, WEAK_VERBS


def check_action_verbs(text_lower):
    findings = []
    score = 0
    max_score = 10

    found_by_category = {}
    total_found = []
    for cat, verbs in ACTION_VERBS_BY_CATEGORY.items():
        matched = [v for v in verbs if re.search(r"\b" + v + r"\w*\b", text_lower)]
        if matched:
            found_by_category[cat] = matched
            total_found.extend(matched)

    verb_count = len(total_found)
    category_count = len(found_by_category)

    if verb_count >= 12:
        score = 10
        findings.append({"type": "pass", "message": f"Outstanding use of action verbs — {verb_count} strong verbs across {category_count} categories"})
    elif verb_count >= 8:
        score = 8
        findings.append({"type": "pass", "message": f"Excellent action verb usage — {verb_count} verbs found in {category_count} categories"})
    elif verb_count >= 5:
        score = 6
        findings.append({"type": "warning", "message": f"Good start with {verb_count} action verbs — aim for 10+ different verbs"})
    elif verb_count >= 2:
        score = 3
        findings.append({"type": "warning", "message": f"Only {verb_count} action verbs found — start every bullet point with a strong action verb"})
    else:
        findings.append({"type": "fail", "message": "Very few action verbs — replace 'was responsible for' with verbs like Developed, Led, Implemented"})

    for cat, verbs in found_by_category.items():
        findings.append({"type": "info", "message": f"{cat}: {', '.join(verbs)}"})

    missing_cats = [c for c in ACTION_VERBS_BY_CATEGORY if c not in found_by_category]
    if missing_cats and len(missing_cats) <= 5:
        suggestions = {}
        for cat in missing_cats[:3]:
            suggestions[cat] = ACTION_VERBS_BY_CATEGORY[cat][:3]
        parts = [f"{cat} ({', '.join(vs)})" for cat, vs in suggestions.items()]
        findings.append({"type": "warning", "message": f"Missing verb categories — try adding: {'; '.join(parts)}"})

    weak_found = [v for v in WEAK_VERBS if v in text_lower]
    if weak_found:
        score = max(0, score - 1)
        findings.append({"type": "fail", "message": f"Weak phrases detected: '{', '.join(weak_found)}' — replace with specific action verbs"})
    else:
        findings.append({"type": "pass", "message": "No weak/passive phrases detected — your language is strong"})

    return round(min(score, max_score), 1), max_score, findings
