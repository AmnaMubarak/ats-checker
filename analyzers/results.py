import re


def check_measurable_results(text, text_lower):
    findings = []
    score = 0
    max_score = 10

    percentages = re.findall(r"\d+[\.\d]*\s*%", text)
    dollars = re.findall(r"\$\s*[\d,]+[\.\d]*[KMBkmb]?|\d+[\.\d]*\s*(?:dollars|USD)", text, re.IGNORECASE)
    people_metrics = re.findall(r"[\d,]+\s*(?:users|clients|customers|members|employees|people|students|attendees|team members|engineers)", text, re.IGNORECASE)
    time_metrics = re.findall(r"[\d,]+\s*(?:hours|days|weeks|months|years|minutes)", text, re.IGNORECASE)
    quantity_metrics = re.findall(r"[\d,]+\s*(?:projects|applications|features|tickets|deployments|releases|reports|repositories|systems|servers|databases)", text, re.IGNORECASE)
    improvement_phrases = re.findall(r"\b(?:increased|decreased|reduced|improved|grew|saved|generated|boosted|cut|raised|doubled|tripled)\b[^.]*?\d+", text, re.IGNORECASE)

    all_metrics = {
        "Percentages": percentages,
        "Financial": dollars,
        "People/Scale": people_metrics,
        "Time": time_metrics,
        "Volume": quantity_metrics,
        "Impact Statements": improvement_phrases,
    }

    total = sum(len(v) for v in all_metrics.values())

    if total >= 8:
        score = 10
        findings.append({"type": "pass", "message": f"Exceptional quantification — {total} measurable results found across your resume"})
    elif total >= 5:
        score = 8
        findings.append({"type": "pass", "message": f"Strong metrics usage — {total} quantifiable results found"})
    elif total >= 3:
        score = 5
        findings.append({"type": "warning", "message": f"Moderate metrics ({total} found) — add numbers to at least 50% of your bullet points"})
    elif total >= 1:
        score = 2
        findings.append({"type": "warning", "message": f"Only {total} measurable result(s) — quantify more achievements for stronger impact"})
    else:
        findings.append({"type": "fail", "message": "No quantifiable results found — this is a major gap. Add numbers, percentages, and dollar amounts"})

    for metric_type, values in all_metrics.items():
        if values:
            display = [v.strip()[:60] for v in values[:3]]
            findings.append({"type": "info", "message": f"{metric_type}: {', '.join(display)}"})

    if not percentages:
        findings.append({"type": "warning", "message": "Tip: Add percentages (e.g., 'Improved performance by 40%', 'Reduced costs by 25%')"})
    if not dollars and not any(w in text_lower for w in ["revenue", "budget", "cost", "savings"]):
        findings.append({"type": "warning", "message": "Tip: Include financial impact where possible (e.g., 'Managed $500K budget', 'Generated $2M revenue')"})

    return round(min(score, max_score), 1), max_score, findings
