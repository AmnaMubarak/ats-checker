from constants import HARD_SKILLS


def check_hard_skills(text_lower):
    findings = []
    score = 0
    max_score = 12

    found_by_category = {}
    total_found = []

    for cat, skills in HARD_SKILLS.items():
        matched = [s for s in skills if s.lower() in text_lower]
        if matched:
            found_by_category[cat] = matched
            total_found.extend(matched)

    skill_count = len(total_found)
    cat_count = len(found_by_category)

    if skill_count >= 12:
        score = 12
        findings.append({"type": "pass", "message": f"Excellent hard skill coverage — {skill_count} technical skills across {cat_count} categories"})
    elif skill_count >= 8:
        score = 10
        findings.append({"type": "pass", "message": f"Strong technical skills — {skill_count} hard skills detected in {cat_count} categories"})
    elif skill_count >= 5:
        score = 7
        findings.append({"type": "warning", "message": f"Decent technical skills ({skill_count}) — add more relevant skills from job descriptions"})
    elif skill_count >= 2:
        score = 4
        findings.append({"type": "warning", "message": f"Limited hard skills ({skill_count}) — technical skills are crucial for ATS filtering"})
    else:
        findings.append({"type": "fail", "message": "Very few technical skills detected — ATS systems heavily weight hard skills for filtering"})

    for cat, skills in found_by_category.items():
        findings.append({"type": "info", "message": f"{cat}: {', '.join(skills)}"})

    missing_cats = [c for c in HARD_SKILLS if c not in found_by_category]
    if missing_cats:
        findings.append({"type": "info", "message": f"Categories not represented: {', '.join(missing_cats[:4])}"})

    return round(min(score, max_score), 1), max_score, findings
