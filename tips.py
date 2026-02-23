def generate_tips(categories, overall_score, text_lower):
    tips = []

    category_scores = {c["name"]: c["percentage"] for c in categories}

    if category_scores.get("Contact Information", 100) < 80:
        tips.append({
            "priority": "high",
            "title": "Complete Your Contact Information",
            "description": "Add missing contact details. Include: professional email, phone number, LinkedIn URL, city/state, and a portfolio link if relevant.",
            "impact": "ATS systems need complete contact info to create your candidate profile."
        })

    if category_scores.get("Hard Skills", 100) < 60:
        tips.append({
            "priority": "high",
            "title": "Add More Technical Skills",
            "description": "List specific tools, technologies, and platforms you've used. Copy exact skill names from the job description.",
            "impact": "ATS keyword matching relies heavily on hard skills — this is often the #1 filter."
        })

    if category_scores.get("Measurable Results", 100) < 60:
        tips.append({
            "priority": "high",
            "title": "Quantify Your Achievements",
            "description": "Add numbers to at least 50% of your bullet points. Include: percentages, dollar amounts, team sizes, project counts, and time saved.",
            "impact": "Resumes with metrics get 40% more interviews than those without."
        })

    if category_scores.get("Action Verbs", 100) < 70:
        tips.append({
            "priority": "medium",
            "title": "Strengthen Your Language",
            "description": "Start every bullet point with a powerful action verb. Use: Developed, Implemented, Led, Designed, Optimized, Achieved, Spearheaded.",
            "impact": "Action verbs signal initiative and impact to both ATS and human reviewers."
        })

    if category_scores.get("Resume Sections", 100) < 80:
        tips.append({
            "priority": "medium",
            "title": "Add Missing Sections",
            "description": "Ensure you have: Summary/Objective, Experience, Education, and Skills at minimum. Add Certifications, Projects, or Awards as bonus sections.",
            "impact": "Standard sections help ATS categorize your information correctly."
        })

    if category_scores.get("Readability", 100) < 70:
        tips.append({
            "priority": "medium",
            "title": "Improve Readability",
            "description": "Shorten long sentences (aim for 10–20 words). Break dense paragraphs into bullet points. Use clear, professional language.",
            "impact": "Recruiters spend 7.4 seconds on initial scan — clear formatting catches their eye."
        })

    if category_scores.get("Formatting & Structure", 100) < 70:
        tips.append({
            "priority": "medium",
            "title": "Optimize Your Formatting",
            "description": "Use consistent bullet points, proper date formats (e.g., 'Jan 2023 – Present'), and keep the resume to 1–2 pages.",
            "impact": "Proper formatting ensures ATS can parse all your information accurately."
        })

    if category_scores.get("Work Experience", 100) < 70:
        tips.append({
            "priority": "high",
            "title": "Strengthen Your Work Experience Section",
            "description": "Add clear job titles, full company names, and proper date ranges (e.g., 'Jan 2022 – Mar 2024'). Each position needs: Title, Company, Dates, and bullet points.",
            "impact": "ATS systems build your career timeline from dates and company names — missing info means broken parsing."
        })

    if category_scores.get("Education", 100) < 60:
        tips.append({
            "priority": "medium",
            "title": "Complete Your Education Details",
            "description": "Include: degree type (Bachelor's, Master's), field of study, university name, and graduation year. Add GPA if 3.0+ or any academic honors.",
            "impact": "Many ATS filters require specific degree levels — missing education data can auto-reject your application."
        })

    if category_scores.get("ATS Compatibility", 100) < 80:
        tips.append({
            "priority": "medium",
            "title": "Improve ATS Compatibility",
            "description": "Use a single-column layout, avoid tables/images, use standard section headings, and save as PDF or DOCX.",
            "impact": "75% of resumes are rejected by ATS before a human sees them."
        })

    if overall_score >= 80 and len(tips) < 2:
        tips.append({
            "priority": "low",
            "title": "Tailor for Each Application",
            "description": "Your resume is well-optimized! To maximize results, customize keywords for each job by mirroring the exact phrases from the job description.",
            "impact": "Tailored resumes are 3x more likely to get past ATS screening."
        })

    if overall_score >= 80:
        tips.append({
            "priority": "low",
            "title": "Keep Your Resume Updated",
            "description": "Update your resume every 3–6 months with new achievements, skills, and metrics. Even small updates keep it fresh.",
            "impact": "Regularly updated resumes reflect continuous growth to recruiters."
        })

    tips.sort(key=lambda t: {"high": 0, "medium": 1, "low": 2}.get(t["priority"], 1))
    return tips[:8]
