import re


def check_work_experience(text, text_lower):
    findings = []
    score = 0
    max_score = 12

    MONTH = r"(?:jan(?:uary)?|feb(?:ruary)?|mar(?:ch)?|apr(?:il)?|may|jun(?:e)?|jul(?:y)?|aug(?:ust)?|sep(?:tember)?|oct(?:ober)?|nov(?:ember)?|dec(?:ember)?)"
    YEAR = r"(?:19|20)\d{2}"

    full_ranges = re.findall(
        rf"{MONTH}\.?\s*{YEAR}\s*[–\-—to]+\s*(?:{MONTH}\.?\s*{YEAR}|present|current|now|ongoing)",
        text, re.IGNORECASE)
    year_only_ranges = re.findall(
        rf"\b{YEAR}\s*[–\-—to]+\s*(?:{YEAR}|present|current|now|ongoing)\b",
        text, re.IGNORECASE)
    all_ranges = full_ranges + year_only_ranges

    if len(full_ranges) >= 2:
        score += 3
        findings.append({"type": "pass", "message": f"{len(full_ranges)} proper date ranges found (Month Year – Month Year) — ideal for ATS"})
    elif len(all_ranges) >= 2:
        score += 2
        findings.append({"type": "warning", "message": f"{len(all_ranges)} date range(s) found but missing month names — use 'Jan 2022 – Mar 2024' format"})
    elif len(all_ranges) == 1:
        score += 1
        findings.append({"type": "warning", "message": "Only 1 date range found — add start/end dates for every position"})
    else:
        findings.append({"type": "fail", "message": "No employment date ranges detected — ATS needs dates to build your work timeline"})

    year_mentions = re.findall(rf"\b({YEAR})\b", text)
    unique_years = sorted(set(year_mentions))
    if len(unique_years) >= 3:
        span = int(unique_years[-1]) - int(unique_years[0])
        score += 1.5
        findings.append({"type": "pass", "message": f"Career spans {span} years ({unique_years[0]}–{unique_years[-1]})"})
    elif len(unique_years) >= 1:
        findings.append({"type": "info", "message": f"Year(s) found: {', '.join(unique_years)}"})

    title_keywords = re.findall(
        r"\b(?:software engineer|web developer|data scientist|product manager|project manager|"
        r"frontend developer|backend developer|full[- ]stack developer|devops engineer|"
        r"ui/?ux designer|graphic designer|business analyst|data analyst|data engineer|"
        r"machine learning engineer|cloud engineer|qa engineer|systems engineer|"
        r"marketing manager|sales manager|operations manager|hr manager|account manager|"
        r"cto|ceo|cfo|coo|vp of\s+\w+|vice president|team lead|tech lead|"
        r"senior\s+\w+\s+\w+|junior\s+\w+|lead\s+\w+|principal\s+\w+|staff\s+\w+|"
        r"head of\s+\w+|director of\s+\w+)\b",
        text, re.IGNORECASE)
    unique_titles = list(set(t.lower().strip() for t in title_keywords))

    if len(unique_titles) >= 3:
        score += 3
        findings.append({"type": "pass", "message": f"Clear job titles detected ({len(unique_titles)}): {', '.join(unique_titles[:6])}"})
    elif len(unique_titles) >= 1:
        score += 1.5
        findings.append({"type": "warning", "message": f"Job title(s) found: {', '.join(unique_titles[:4])} — ensure each position has a clear title"})
    else:
        findings.append({"type": "fail", "message": "No recognizable job titles — use standard titles like 'Software Engineer', 'Project Manager'"})

    company_suffixes = re.findall(
        r"\b\w[\w\s&]{1,30}(?:Inc\.?|LLC|Ltd\.?|Corp\.?|Corporation|Company|Co\.|"
        r"Technologies|Solutions|Services|Group|Labs|Studio|Consulting|Partners|"
        r"Enterprises|Systems|Software|Digital|Media|Agency|Foundation|Institute)\b",
        text, re.IGNORECASE)
    unique_companies = list(set(c.strip() for c in company_suffixes))

    if len(unique_companies) >= 2:
        score += 2.5
        names = [c[:40] for c in unique_companies[:5]]
        findings.append({"type": "pass", "message": f"Companies identified ({len(unique_companies)}): {', '.join(names)}"})
    elif len(unique_companies) == 1:
        score += 1.5
        findings.append({"type": "warning", "message": f"1 company found: {unique_companies[0][:40]} — make sure all employers are clearly listed"})
    else:
        findings.append({"type": "fail", "message": "No clear company names detected — list full company names (e.g., 'Google LLC', 'Acme Technologies')"})

    has_current = bool(re.search(r"\b(?:present|current|ongoing)\b", text, re.IGNORECASE))
    if has_current:
        score += 1
        findings.append({"type": "pass", "message": "Current position indicated ('Present') — ATS understands you're currently employed"})
    else:
        findings.append({"type": "info", "message": "No 'Present' date found — if currently employed, mark your latest role as '... – Present'"})

    location_pattern = re.findall(r"\b[A-Z][a-z]+,\s*[A-Z]{2}\b|\b(?:remote|hybrid|on-?site)\b", text, re.IGNORECASE)
    if location_pattern:
        score += 0.5
        findings.append({"type": "pass", "message": f"Work location(s) detected: {', '.join(set(l.strip() for l in location_pattern[:4]))}"})

    return round(min(score, max_score), 1), max_score, findings
