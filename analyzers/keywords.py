from collections import Counter
from constants import HARD_SKILLS, SOFT_SKILLS


def check_keyword_optimization(text_lower):
    findings = []
    score = 0
    max_score = 10

    all_keywords = []
    for skills in HARD_SKILLS.values():
        all_keywords.extend(skills)
    for skills in SOFT_SKILLS.values():
        all_keywords.extend(skills)

    found_keywords = list(set(kw for kw in all_keywords if kw.lower() in text_lower))
    keyword_count = len(found_keywords)

    if keyword_count >= 20:
        score = 10
        findings.append({"type": "pass", "message": f"Outstanding keyword density — {keyword_count} ATS-relevant keywords detected"})
    elif keyword_count >= 14:
        score = 8
        findings.append({"type": "pass", "message": f"Strong keyword presence — {keyword_count} keywords that ATS systems scan for"})
    elif keyword_count >= 8:
        score = 5
        findings.append({"type": "warning", "message": f"Moderate keyword density ({keyword_count}) — tailor keywords to match specific job descriptions"})
    elif keyword_count >= 4:
        score = 3
        findings.append({"type": "warning", "message": f"Low keyword density ({keyword_count}) — you may be filtered out by ATS keyword matching"})
    else:
        findings.append({"type": "fail", "message": "Very few ATS keywords — your resume may not pass keyword-based screening"})

    word_freq = Counter(text_lower.split())
    repeated_keywords = [(kw, word_freq.get(kw, 0)) for kw in found_keywords if word_freq.get(kw, 0) >= 3]
    repeated_keywords.sort(key=lambda x: x[1], reverse=True)

    if repeated_keywords:
        top = [f"{kw} ({count}x)" for kw, count in repeated_keywords[:5]]
        findings.append({"type": "info", "message": f"Most emphasized keywords: {', '.join(top)}"})

    found_keywords.sort()
    chunk_size = 12
    for i in range(0, min(len(found_keywords), 24), chunk_size):
        chunk = found_keywords[i:i + chunk_size]
        findings.append({"type": "info", "message": f"Keywords detected: {', '.join(chunk)}"})

    findings.append({"type": "info",
                      "message": "Pro tip: Copy keywords directly from the job description you're applying to — ATS systems match exact phrases"})

    return round(min(score, max_score), 1), max_score, findings
