import re


def check_education(text, text_lower):
    findings = []
    score = 0
    max_score = 10

    degree_patterns = {
        "Doctorate/PhD": r"\b(?:ph\.?d\.?|doctorate|doctor of)\b",
        "Master's": r"\b(?:master(?:'?s)?\s+(?:of|in|degree)|msc|mba|m\.?eng\.?|m\.?tech\.?)\b",
        "Bachelor's": r"\b(?:bachelor(?:'?s)?\s+(?:of|in|degree)|bsc|b\.?eng\.?|b\.?tech\.?|b\.?s\.?\s+in)\b",
        "Associate's": r"\b(?:associate(?:'?s)?\s+(?:of|in|degree))\b",
        "Diploma": r"\b(?:diploma\s+in|diploma\s+of)\b",
        "MS": r"\b(?:master of science|master of science in)\b",
        "MBA": r"\b(?:master of business administration|master of business administration in)\b",
        "MEng": r"\b(?:master of engineering|master of engineering in)\b",
        "MTECH": r"\b(?:master of technology|master of technology in)\b",
        "MBA": r"\b(?:master of business administration|master of business administration in)\b",
        "MBA": r"\b(?:master of business administration|master of business administration in)\b",
    }

    found_degrees = []
    for deg_name, pattern in degree_patterns.items():
        if re.search(pattern, text, re.IGNORECASE):
            found_degrees.append(deg_name)

    if found_degrees:
        score += 3
        findings.append({"type": "pass", "message": f"Degree level detected: {', '.join(found_degrees)}"})
    else:
        findings.append({"type": "fail", "message": "No degree type found — specify your degree (e.g., Bachelor of Science, Master of Arts, MBA)"})

    fields = re.findall(
        r"\b(?:computer science|information technology|software engineering|"
        r"electrical engineering|mechanical engineering|civil engineering|"
        r"data science|mathematics|statistics|physics|chemistry|biology|"
        r"business administration|finance|accounting|economics|marketing|"
        r"communications|psychology|political science|english|history|"
        r"graphic design|information systems|cybersecurity|"
        r"business analytics|data analytics|data engineering|data science|"
        r"software engineering|web development|mobile development|"
        r"artificial intelligence|machine learning)\b",
        text, re.IGNORECASE)
    unique_fields = list(set(f.lower() for f in fields))

    if unique_fields:
        score += 2
        findings.append({"type": "pass", "message": f"Field of study: {', '.join(unique_fields[:3])}"})
    else:
        findings.append({"type": "warning", "message": "No field of study detected — include your major (e.g., 'BS in Computer Science')"})

    uni_keywords = re.findall(
        r"\b(?:university|college|institute|school|academy|polytechnic)\s+(?:of\s+)?[A-Z][\w\s,]{2,40}",
        text, re.IGNORECASE)
    named_unis = re.findall(
        r"\b(?:MIT|Stanford|Harvard|Oxford|Cambridge|Berkeley|UCLA|NYU|Georgia Tech|"
        r"Carnegie Mellon|Caltech|Princeton|Yale|Columbia|Cornell|UPenn|"
        r"IIT|LUMS|NUST|FAST|COMSATS|NED|UET|GIKI|PIEAS)\b",
        text, re.IGNORECASE)
    all_unis = list(set([u.strip()[:50] for u in uni_keywords] + [u.strip() for u in named_unis]))

    if all_unis:
        score += 2
        findings.append({"type": "pass", "message": f"Institution(s): {', '.join(all_unis[:3])}"})
    else:
        findings.append({"type": "warning", "message": "No institution name detected — include your university or college name"})

    edu_section = ""
    edu_start = re.search(r"\b(?:education|academic|qualification)\b", text_lower)
    if edu_start:
        edu_section = text[edu_start.start():edu_start.start() + 800]

    grad_years = re.findall(r"\b(20\d{2}|19\d{2})\b", edu_section if edu_section else text[-600:])
    if grad_years:
        score += 1.5
        findings.append({"type": "pass", "message": f"Education year(s): {', '.join(sorted(set(grad_years)))}"})
    else:
        findings.append({"type": "warning", "message": "No graduation year found in education section — add your graduation year or expected graduation"})

    gpa_match = re.search(r"\b(?:gpa|cgpa|grade)[:\s]*(\d+\.?\d*)\s*/?\s*(\d+\.?\d*)?\b", text, re.IGNORECASE)
    honors = re.findall(r"\b(?:cum laude|magna cum laude|summa cum laude|dean'?s list|honor(?:s|'s)?\s*(?:roll|society)?|distinction|first class|second class|merit)\b", text, re.IGNORECASE)

    if gpa_match:
        gpa_str = gpa_match.group(0).strip()
        score += 1
        findings.append({"type": "pass", "message": f"GPA listed: {gpa_str}"})
    elif honors:
        score += 1
        findings.append({"type": "pass", "message": f"Academic honors: {', '.join(set(h.lower() for h in honors))}"})
    else:
        findings.append({"type": "info", "message": "No GPA or honors found — include GPA if 3.0+ or list academic honors"})

    return round(min(score, max_score), 1), max_score, findings
