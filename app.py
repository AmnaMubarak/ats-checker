import os
import re
import math
import string
from collections import Counter
from flask import Flask, request, jsonify, render_template, Response, url_for
from werkzeug.utils import secure_filename
from PyPDF2 import PdfReader
from docx import Document

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 5 * 1024 * 1024

IS_VERCEL = os.environ.get("VERCEL") or os.environ.get("AWS_LAMBDA_FUNCTION_NAME")
UPLOAD_DIR = "/tmp/uploads" if IS_VERCEL else os.path.join(os.path.dirname(__file__), "uploads")
app.config["UPLOAD_FOLDER"] = UPLOAD_DIR

ALLOWED_EXTENSIONS = {"pdf", "docx"}
os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


# ---------------------------------------------------------------------------
# Text extraction
# ---------------------------------------------------------------------------

def extract_text_from_pdf(filepath):
    text = ""
    reader = PdfReader(filepath)
    num_pages = len(reader.pages)
    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            text += page_text + "\n"
    return text, num_pages


def extract_text_from_docx(filepath):
    doc = Document(filepath)
    text = "\n".join(p.text for p in doc.paragraphs)
    page_estimate = max(1, len(text.split()) // 450)
    return text, page_estimate


def extract_text(filepath):
    ext = filepath.rsplit(".", 1)[1].lower()
    if ext == "pdf":
        return extract_text_from_pdf(filepath)
    elif ext == "docx":
        return extract_text_from_docx(filepath)
    return "", 0


# ---------------------------------------------------------------------------
# Data dictionaries
# ---------------------------------------------------------------------------

SECTION_KEYWORDS = {
    "contact": ["email", "phone", "address", "linkedin", "github", "portfolio", "website", "contact"],
    "summary": ["summary", "objective", "profile", "about me", "professional summary",
                 "career objective", "career summary", "professional profile", "executive summary"],
    "experience": ["experience", "work experience", "employment", "professional experience",
                    "work history", "employment history", "relevant experience"],
    "education": ["education", "academic", "qualification", "degree", "university",
                   "college", "academic background", "educational background"],
    "skills": ["skills", "technical skills", "competencies", "proficiencies",
               "core competencies", "areas of expertise", "key skills", "skill set"],
    "certifications": ["certifications", "certificates", "licenses", "accreditations",
                        "professional certifications", "professional development"],
    "projects": ["projects", "personal projects", "academic projects", "key projects",
                  "notable projects", "selected projects"],
    "awards": ["awards", "honors", "achievements", "recognition", "accomplishments"],
    "languages": ["languages", "language proficiency", "language skills"],
    "volunteer": ["volunteer", "volunteering", "community service", "extracurricular"],
    "references": ["references", "referees"],
    "publications": ["publications", "research", "papers"],
}

ACTION_VERBS_BY_CATEGORY = {
    "Leadership": ["led", "directed", "managed", "supervised", "oversaw", "headed",
                    "spearheaded", "coordinated", "mentored", "guided", "delegated", "chaired"],
    "Achievement": ["achieved", "exceeded", "surpassed", "earned", "attained", "accomplished",
                     "awarded", "won", "outperformed", "delivered"],
    "Technical": ["developed", "engineered", "built", "designed", "implemented", "programmed",
                   "coded", "configured", "deployed", "automated", "architected", "integrated",
                   "debugged", "tested", "maintained"],
    "Communication": ["presented", "authored", "published", "documented", "reported",
                       "communicated", "articulated", "briefed", "advocated", "negotiated"],
    "Improvement": ["improved", "enhanced", "increased", "optimized", "streamlined",
                     "modernized", "accelerated", "transformed", "revamped", "upgraded",
                     "refined", "restructured"],
    "Analysis": ["analyzed", "assessed", "evaluated", "researched", "investigated",
                  "examined", "audited", "forecasted", "identified", "measured", "quantified"],
    "Creation": ["created", "established", "founded", "initiated", "launched", "pioneered",
                  "introduced", "generated", "formulated", "devised", "invented"],
    "Operations": ["executed", "administered", "facilitated", "organized", "planned",
                    "produced", "processed", "consolidated", "resolved", "performed",
                    "collaborated", "conducted", "trained"],
}

ALL_ACTION_VERBS = []
for verbs in ACTION_VERBS_BY_CATEGORY.values():
    ALL_ACTION_VERBS.extend(verbs)

WEAK_VERBS = ["helped", "assisted", "tried", "worked on", "was responsible for",
              "responsible for", "duties included", "tasked with", "participated in",
              "involved in", "handled"]

HARD_SKILLS = {
    "Programming Languages": ["python", "java", "javascript", "typescript", "c++", "c#", "ruby",
                               "php", "swift", "kotlin", "golang", "rust", "scala", "r ", "matlab"],
    "Web Technologies": ["html", "css", "react", "angular", "vue", "node.js", "nodejs", "express",
                          "django", "flask", "spring", "asp.net", "next.js", "tailwind", "bootstrap",
                          "graphql", "rest api", "restful"],
    "Databases": ["sql", "mysql", "postgresql", "mongodb", "redis", "elasticsearch",
                   "dynamodb", "oracle", "firebase", "cassandra", "sqlite"],
    "Cloud & DevOps": ["aws", "azure", "gcp", "google cloud", "docker", "kubernetes",
                        "jenkins", "terraform", "ansible", "ci/cd", "github actions", "gitlab"],
    "Data & AI": ["machine learning", "deep learning", "data analysis", "data science",
                   "tensorflow", "pytorch", "pandas", "numpy", "tableau", "power bi",
                   "nlp", "computer vision", "artificial intelligence", "big data", "spark", "hadoop"],
    "Tools & Software": ["git", "jira", "confluence", "figma", "adobe", "photoshop",
                          "excel", "powerpoint", "microsoft office", "slack", "trello",
                          "postman", "vs code", "intellij"],
    "Security": ["cybersecurity", "penetration testing", "encryption", "oauth", "ssl",
                  "firewall", "siem", "vulnerability", "compliance"],
    "Mobile": ["android", "ios", "react native", "flutter", "swift", "kotlin"],
}

SOFT_SKILLS = {
    "Leadership": ["leadership", "team lead", "mentorship", "delegation", "decision making",
                    "strategic thinking", "vision", "coaching"],
    "Communication": ["communication", "presentation", "public speaking", "writing",
                       "negotiation", "interpersonal", "active listening", "storytelling"],
    "Problem Solving": ["problem solving", "critical thinking", "analytical", "troubleshooting",
                         "innovation", "creative thinking", "root cause analysis"],
    "Collaboration": ["teamwork", "collaboration", "cross-functional", "stakeholder management",
                       "partnership", "relationship building", "conflict resolution"],
    "Management": ["project management", "time management", "agile", "scrum", "kanban",
                    "resource management", "risk management", "budget management", "planning"],
    "Adaptability": ["adaptability", "flexibility", "fast learner", "quick learner",
                      "self-motivated", "proactive", "detail-oriented", "multitasking"],
}

UNPROFESSIONAL_EMAIL_WORDS = ["cute", "hot", "sexy", "babe", "cool", "princess",
                               "prince", "love", "angel", "devil", "420", "69",
                               "xxx", "gamer", "ninja", "swag", "yolo"]

ATS_UNFRIENDLY_CHARS = ["\u2022", "\u25cf", "\u25aa", "\u25a0", "\u2192", "\u2190",
                         "\u2605", "\u2606", "\u2713", "\u2717", "\u25b6", "\u25c0",
                         "\u2764", "\u2603", "\u263a"]


# ---------------------------------------------------------------------------
# Analysis functions — each returns (score, max_score, findings)
# ---------------------------------------------------------------------------

def check_contact_info(text, text_lower):
    findings = []
    score = 0
    max_score = 12

    # PDFs often extract text with extra spaces, broken URLs, or missing dots.
    # Collapse whitespace for URL detection while keeping original for other checks.
    text_collapsed = re.sub(r"\s+", " ", text)
    text_no_spaces = re.sub(r"\s+", "", text_lower)

    # --- Email ---
    email_match = re.search(r"[a-zA-Z0-9._%+\-]+\s*@\s*[a-zA-Z0-9.\-]+\.\s*[a-zA-Z]{2,}", text)
    if not email_match:
        email_match = re.search(r"[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}", text_collapsed)

    # --- Phone ---
    phone_match = re.search(r"[\+]?[\d\s\-\(\)]{7,15}", text)

    # --- LinkedIn: handle PDF extraction quirks ---
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

    # --- GitHub: handle PDF extraction quirks ---
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

    # --- Website / Portfolio ---
    website_match = (
        re.search(r"(?:portfolio|website|http|www\.)\S+", text, re.IGNORECASE) or
        re.search(r"(?:portfolio|website|http|www\.)\S+", text_collapsed, re.IGNORECASE) or
        re.search(r"\b(?:portfolio|website)\b", text_lower)
    )

    # --- Location ---
    location_match = (
        re.search(r"\b(?:city|state|country|zip|located in|based in|remote|hybrid)\b", text_lower) or
        re.search(r"\b[A-Z][a-z]+,\s*[A-Z]{2}\b", text) or
        re.search(r"\b[A-Z][a-z]+,\s*[A-Z][a-z]+\b", text)
    )

    # --- Score: Email ---
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

    # --- Score: Phone ---
    if phone_match:
        score += 3
        findings.append({"type": "pass", "message": "Phone number detected"})
    else:
        findings.append({"type": "fail", "message": "No phone number found — recruiters need a way to call you"})

    # --- Score: LinkedIn ---
    if linkedin_match:
        score += 2
        if linkedin_is_keyword_only:
            findings.append({"type": "pass", "message": "LinkedIn reference found (URL may be hyperlinked in original — PDF extraction can break links)"})
        else:
            findings.append({"type": "pass", "message": "LinkedIn profile URL detected"})
    else:
        score += 0.5
        findings.append({"type": "warning", "message": "No LinkedIn URL — 87% of recruiters use LinkedIn; add your profile link"})

    # --- Score: GitHub / Portfolio ---
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
        score += 0.5
        findings.append({"type": "info", "message": "No portfolio/GitHub link — consider adding one to stand out"})

    if location_match:
        score += 2
        findings.append({"type": "pass", "message": "Location information detected"})
    else:
        score += 0.5
        findings.append({"type": "warning", "message": "No location detected — some employers filter by location, add city/state or 'Remote'"})

    return round(min(score, max_score), 1), max_score, findings


def check_sections(text_lower):
    findings = []
    score = 0
    max_score = 15

    critical = {"experience": 4, "education": 4, "skills": 4}
    important = {"summary": 1.5}
    nice_to_have = {"certifications": 0.5, "projects": 0.5, "awards": 0.3,
                    "languages": 0.3, "volunteer": 0.2}

    found_sections = []
    missing_critical = []
    missing_important = []

    for section, pts in critical.items():
        found = any(kw in text_lower for kw in SECTION_KEYWORDS[section])
        if found:
            score += pts
            found_sections.append(section.title())
            findings.append({"type": "pass", "message": f"'{section.title()}' section found"})
        else:
            missing_critical.append(section.title())
            findings.append({"type": "fail", "message": f"Missing '{section.title()}' section — this is essential for ATS parsing"})

    for section, pts in important.items():
        found = any(kw in text_lower for kw in SECTION_KEYWORDS[section])
        if found:
            score += pts
            found_sections.append(section.title())
            findings.append({"type": "pass", "message": f"'{section.title()}' section found — helps recruiters quickly assess your profile"})
        else:
            missing_important.append(section.title())
            score += 0.3
            findings.append({"type": "warning", "message": f"No '{section.title()}' section — a strong summary can boost recruiter interest by 36%"})

    nice_found = 0
    for section, pts in nice_to_have.items():
        found = any(kw in text_lower for kw in SECTION_KEYWORDS[section])
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


def check_formatting(text, num_pages):
    findings = []
    score = 0
    max_score = 13

    words = text.split()
    word_count = len(words)
    lines = text.strip().split("\n")
    non_empty_lines = [l for l in lines if l.strip()]

    # Page count
    if num_pages == 1:
        score += 2
        findings.append({"type": "pass", "message": "Single-page resume — ideal for most positions"})
    elif num_pages == 2:
        score += 2
        findings.append({"type": "pass", "message": "Two-page resume — acceptable for experienced professionals"})
    elif num_pages >= 3:
        score += 0.5
        findings.append({"type": "warning", "message": f"{num_pages}-page resume detected — keep it to 1–2 pages unless you have 10+ years of experience"})

    # Word count
    if 400 <= word_count <= 800:
        score += 2
        findings.append({"type": "pass", "message": f"Optimal word count: {word_count} words (ideal range: 400–800)"})
    elif 300 <= word_count < 400:
        score += 1.5
        findings.append({"type": "warning", "message": f"Slightly short ({word_count} words) — aim for 400–800 words to provide enough detail"})
    elif 800 < word_count <= 1100:
        score += 1.5
        findings.append({"type": "warning", "message": f"Slightly long ({word_count} words) — consider trimming less relevant details"})
    elif word_count < 300:
        score += 0.5
        findings.append({"type": "fail", "message": f"Too short ({word_count} words) — your resume needs more content to be competitive"})
    else:
        score += 0.5
        findings.append({"type": "fail", "message": f"Too long ({word_count} words) — recruiters spend 7 seconds on initial scan, be concise"})

    # Bullet points
    bullet_chars = ["•", "●", "▪", "■", "-", "–", "→", "*", "◦", "‣", "►"]
    bullet_lines = sum(1 for l in non_empty_lines if any(l.strip().startswith(c) for c in bullet_chars))
    bullet_ratio = bullet_lines / max(len(non_empty_lines), 1)

    if bullet_ratio > 0.2:
        score += 3
        findings.append({"type": "pass", "message": f"Excellent bullet point usage ({bullet_lines} bullet lines, {round(bullet_ratio * 100)}% of content)"})
    elif bullet_ratio > 0.1:
        score += 2
        findings.append({"type": "pass", "message": f"Good bullet usage ({bullet_lines} bullets) — could add a few more for readability"})
    elif bullet_ratio > 0.03:
        score += 1
        findings.append({"type": "warning", "message": f"Limited bullet points ({bullet_lines} found) — restructure experience as bullet points for better ATS parsing"})
    else:
        findings.append({"type": "fail", "message": "Almost no bullet points — ATS systems and recruiters strongly prefer bulleted experience"})

    # Dates
    year_dates = re.findall(r"\b(20\d{2}|19\d{2})\b", text)
    month_names = re.findall(r"\b(jan(?:uary)?|feb(?:ruary)?|mar(?:ch)?|apr(?:il)?|may|jun(?:e)?|jul(?:y)?|aug(?:ust)?|sep(?:tember)?|oct(?:ober)?|nov(?:ember)?|dec(?:ember)?)\b", text, re.IGNORECASE)
    date_ranges = re.findall(r"(?:present|current|ongoing)", text, re.IGNORECASE)

    if year_dates and month_names:
        score += 3
        findings.append({"type": "pass", "message": f"Proper date formatting ({len(year_dates)} years, {len(month_names)} months detected)"})
        if date_ranges:
            findings.append({"type": "pass", "message": "Current position indicated with 'Present' — ATS can parse employment timeline"})
    elif year_dates:
        score += 2
        findings.append({"type": "warning", "message": f"Year dates found ({len(year_dates)}) but no month names — use 'Jan 2023 – Present' format for best ATS parsing"})
    else:
        findings.append({"type": "fail", "message": "No date information detected — add employment and education dates (e.g., 'Sep 2021 – Jun 2024')"})

    # Line length consistency
    long_lines = sum(1 for l in non_empty_lines if len(l.strip()) > 120)
    if long_lines > len(non_empty_lines) * 0.3:
        score += 0.5
        findings.append({"type": "warning", "message": f"{long_lines} very long lines detected — break up dense paragraphs into shorter bullet points"})
    else:
        score += 1.5
        findings.append({"type": "pass", "message": "Content has good line-length distribution — readable for both ATS and humans"})

    # ALL CAPS overuse
    caps_lines = sum(1 for l in non_empty_lines if l.strip().isupper() and len(l.strip()) > 3)
    if caps_lines > 6:
        findings.append({"type": "warning", "message": f"Excessive ALL CAPS text ({caps_lines} lines) — use title case for headings instead"})
    elif caps_lines > 0:
        score += 0.5
        findings.append({"type": "pass", "message": "Appropriate use of capitalization for section headings"})

    return round(min(score, max_score), 1), max_score, findings


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

    # Weak verbs check
    weak_found = [v for v in WEAK_VERBS if v in text_lower]
    if weak_found:
        score = max(0, score - 1)
        findings.append({"type": "fail", "message": f"Weak phrases detected: '{', '.join(weak_found)}' — replace with specific action verbs"})
    else:
        findings.append({"type": "pass", "message": "No weak/passive phrases detected — your language is strong"})

    return round(min(score, max_score), 1), max_score, findings


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


def check_work_experience(text, text_lower):
    findings = []
    score = 0
    max_score = 12

    MONTH = r"(?:jan(?:uary)?|feb(?:ruary)?|mar(?:ch)?|apr(?:il)?|may|jun(?:e)?|jul(?:y)?|aug(?:ust)?|sep(?:tember)?|oct(?:ober)?|nov(?:ember)?|dec(?:ember)?)"
    YEAR = r"(?:19|20)\d{2}"

    # --- Date ranges (e.g. "Jan 2020 – Mar 2023", "2019 - 2021", "Aug 2022 – Present") ---
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

    # --- Years & career span ---
    year_mentions = re.findall(rf"\b({YEAR})\b", text)
    unique_years = sorted(set(year_mentions))
    if len(unique_years) >= 3:
        span = int(unique_years[-1]) - int(unique_years[0])
        score += 1.5
        findings.append({"type": "pass", "message": f"Career spans {span} years ({unique_years[0]}–{unique_years[-1]})"})
    elif len(unique_years) >= 1:
        score += 0.5
        findings.append({"type": "info", "message": f"Year(s) found: {', '.join(unique_years)}"})

    # --- Job titles ---
    title_keywords = re.findall(
        r"\b(?:software engineer|web developer|data scientist|product manager|project manager|"
        r"frontend developer|backend developer|full[- ]stack developer|devops engineer|"
        r"ui/?ux designer|graphic designer|business analyst|data analyst|data engineer|"
        r"machine learning engineer|cloud engineer|qa engineer|systems engineer|"
        r"marketing manager|sales manager|operations manager|hr manager|"
        r"cto|ceo|cfo|coo|vp of|vice president|director|team lead|tech lead|"
        r"engineer|developer|designer|manager|analyst|consultant|coordinator|"
        r"specialist|administrator|architect|intern|associate|senior|junior|"
        r"principal|staff|head of)\b",
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

    # --- Company names ---
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
        score += 0.5
        findings.append({"type": "warning", "message": "No clear company names detected — list full company names (e.g., 'Google LLC', 'Acme Technologies')"})

    # --- Present / current role ---
    has_current = bool(re.search(r"\b(?:present|current|ongoing|now)\b", text, re.IGNORECASE))
    if has_current:
        score += 1
        findings.append({"type": "pass", "message": "Current position indicated ('Present') — ATS understands you're currently employed"})
    else:
        score += 0.5
        findings.append({"type": "info", "message": "No 'Present' date found — if currently employed, mark your latest role as '... – Present'"})

    # --- Location ---
    location_pattern = re.findall(r"\b[A-Z][a-z]+,\s*[A-Z]{2}\b|\b(?:remote|hybrid|on-?site)\b", text, re.IGNORECASE)
    if location_pattern:
        score += 0.5
        findings.append({"type": "pass", "message": f"Work location(s) detected: {', '.join(set(l.strip() for l in location_pattern[:4]))}"})

    return round(min(score, max_score), 1), max_score, findings


def check_education(text, text_lower):
    findings = []
    score = 0
    max_score = 10

    # --- Degree type ---
    degree_patterns = {
        "Doctorate/PhD": r"\b(?:ph\.?d\.?|doctorate|doctor of)\b",
        "Master's": r"\b(?:master(?:'?s)?|m\.?s\.?|m\.?a\.?|msc|mba|m\.?eng\.?|m\.?tech\.?)\b",
        "Bachelor's": r"\b(?:bachelor(?:'?s)?|b\.?s\.?|b\.?a\.?|bsc|b\.?eng\.?|b\.?tech\.?)\b",
        "Associate's": r"\b(?:associate(?:'?s)?|a\.?s\.?|a\.?a\.?)\b",
        "Diploma": r"\b(?:diploma|certificate|certification)\b",
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

    # --- Field of study ---
    fields = re.findall(
        r"\b(?:computer science|information technology|software engineering|"
        r"electrical engineering|mechanical engineering|civil engineering|"
        r"data science|mathematics|statistics|physics|chemistry|biology|"
        r"business administration|finance|accounting|economics|marketing|"
        r"communications|psychology|political science|english|history|"
        r"graphic design|information systems|cybersecurity|"
        r"artificial intelligence|machine learning)\b",
        text, re.IGNORECASE)
    unique_fields = list(set(f.lower() for f in fields))

    if unique_fields:
        score += 2
        findings.append({"type": "pass", "message": f"Field of study: {', '.join(unique_fields[:3])}"})
    else:
        score += 0.5
        findings.append({"type": "warning", "message": "No field of study detected — include your major (e.g., 'BS in Computer Science')"})

    # --- University / institution name ---
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
        score += 0.5
        findings.append({"type": "warning", "message": "No institution name detected — include your university or college name"})

    # --- Graduation year ---
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

    # --- GPA / honors ---
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
        score += 0.5
        findings.append({"type": "info", "message": "No GPA or honors found — include GPA if 3.0+ or list academic honors"})

    return round(min(score, max_score), 1), max_score, findings


def check_readability(text):
    findings = []
    score = 0
    max_score = 8

    sentences = re.split(r'[.!?]+', text)
    sentences = [s.strip() for s in sentences if len(s.strip().split()) > 2]

    if not sentences:
        findings.append({"type": "warning", "message": "Could not analyze sentence structure"})
        return 4, max_score, findings

    word_counts = [len(s.split()) for s in sentences]
    avg_sentence_len = sum(word_counts) / len(word_counts) if word_counts else 0

    if 10 <= avg_sentence_len <= 20:
        score += 3
        findings.append({"type": "pass", "message": f"Good sentence length — avg {round(avg_sentence_len, 1)} words per sentence (ideal: 10–20)"})
    elif avg_sentence_len < 10:
        score += 2
        findings.append({"type": "pass", "message": f"Concise writing — avg {round(avg_sentence_len, 1)} words per sentence (clear and scannable)"})
    else:
        score += 1
        findings.append({"type": "warning", "message": f"Long sentences — avg {round(avg_sentence_len, 1)} words. Break complex sentences into shorter ones"})

    long_sentences = sum(1 for w in word_counts if w > 25)
    if long_sentences == 0:
        score += 2
        findings.append({"type": "pass", "message": "No overly long sentences — maintains recruiter attention"})
    elif long_sentences <= 3:
        score += 1
        findings.append({"type": "warning", "message": f"{long_sentences} sentence(s) over 25 words — consider shortening for clarity"})
    else:
        findings.append({"type": "fail", "message": f"{long_sentences} sentences exceed 25 words — recruiters scan, not read; keep it concise"})

    words = text.lower().split()
    complex_words = sum(1 for w in words if len(w) > 12)
    complex_ratio = complex_words / max(len(words), 1)

    if complex_ratio < 0.05:
        score += 1.5
        findings.append({"type": "pass", "message": "Clear vocabulary — professional yet accessible language"})
    elif complex_ratio < 0.1:
        score += 1
        findings.append({"type": "pass", "message": "Vocabulary is mostly clear with some technical jargon (appropriate for specialized roles)"})
    else:
        score += 0.5
        findings.append({"type": "warning", "message": "Heavy use of complex words — ensure jargon is industry-standard and necessary"})

    # Paragraph density
    paragraphs = text.split("\n\n")
    long_paras = sum(1 for p in paragraphs if len(p.split()) > 60)
    if long_paras == 0:
        score += 1.5
        findings.append({"type": "pass", "message": "Good content density — no large text blocks that overwhelm readers"})
    else:
        score += 0.5
        findings.append({"type": "warning", "message": f"{long_paras} dense paragraph(s) found — break into bullet points for better readability"})

    return round(min(score, max_score), 1), max_score, findings


def check_ats_compatibility(text, file_ext):
    findings = []
    score = 0
    max_score = 8

    if file_ext == "pdf":
        score += 2
        findings.append({"type": "pass", "message": "PDF format — universally accepted by ATS systems"})
    elif file_ext == "docx":
        score += 2
        findings.append({"type": "pass", "message": "DOCX format — excellent ATS compatibility (preferred by many systems)"})

    special_chars = [c for c in ATS_UNFRIENDLY_CHARS if c in text]
    if not special_chars:
        score += 2
        findings.append({"type": "pass", "message": "No problematic special characters — clean text for ATS parsing"})
    elif len(special_chars) <= 3:
        score += 1
        findings.append({"type": "warning", "message": f"Some special characters found that may not parse correctly in all ATS systems"})
    else:
        findings.append({"type": "fail", "message": "Multiple special characters detected — replace symbols with standard text equivalents"})

    header_footer_keywords = ["page 1", "page 2", "page 3", "header", "footer",
                               "confidential", "curriculum vitae"]
    found_hf = [kw for kw in header_footer_keywords if kw in text.lower()]
    if not found_hf:
        score += 1.5
        findings.append({"type": "pass", "message": "No headers/footers detected — ATS often misreads content in headers/footers"})
    else:
        score += 0.5
        findings.append({"type": "warning", "message": "Possible header/footer content — some ATS systems skip header/footer areas"})

    table_indicators = re.findall(r"\t{2,}|\s{4,}\S+\s{4,}\S+", text)
    if len(table_indicators) > 5:
        findings.append({"type": "warning", "message": "Possible table/column layout detected — ATS may scramble multi-column layouts; use single-column format"})
    else:
        score += 1.5
        findings.append({"type": "pass", "message": "Layout appears ATS-friendly — no complex table structures detected"})

    image_indicators = re.findall(r"\[image\]|\[photo\]|\[logo\]|\.(?:png|jpg|jpeg|gif|svg)\b", text, re.IGNORECASE)
    if image_indicators:
        findings.append({"type": "warning", "message": "Image references detected — ATS cannot read images; ensure all info is in text form"})
    else:
        score += 1
        findings.append({"type": "pass", "message": "No image-only content detected — all content is text-based and parseable"})

    return round(min(score, max_score), 1), max_score, findings


def check_consistency(text):
    findings = []
    score = 0
    max_score = 7

    # Tense consistency
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

    # Point of view (should not have "I", "my", "me")
    first_person = re.findall(r"\b(?:I|my|me|myself)\b", text)
    if len(first_person) == 0:
        score += 2.5
        findings.append({"type": "pass", "message": "No first-person pronouns — correct resume writing style"})
    elif len(first_person) <= 3:
        score += 1.5
        findings.append({"type": "warning", "message": f"Found {len(first_person)} first-person pronoun(s) (I/my/me) — resumes should omit these"})
    else:
        findings.append({"type": "fail", "message": f"{len(first_person)} first-person pronouns found — remove all 'I', 'my', 'me' from your resume"})

    # Abbreviation consistency
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

    # Keyword repetition analysis
    word_freq = Counter(text_lower.split())
    repeated_keywords = [(kw, word_freq.get(kw, 0)) for kw in found_keywords if word_freq.get(kw, 0) >= 3]
    repeated_keywords.sort(key=lambda x: x[1], reverse=True)

    if repeated_keywords:
        top = [f"{kw} ({count}x)" for kw, count in repeated_keywords[:5]]
        findings.append({"type": "info", "message": f"Most emphasized keywords: {', '.join(top)}"})

    # Show found keywords grouped
    found_keywords.sort()
    chunk_size = 12
    for i in range(0, min(len(found_keywords), 24), chunk_size):
        chunk = found_keywords[i:i + chunk_size]
        findings.append({"type": "info", "message": f"Keywords detected: {', '.join(chunk)}"})

    findings.append({"type": "info",
                      "message": "Pro tip: Copy keywords directly from the job description you're applying to — ATS systems match exact phrases"})

    return round(min(score, max_score), 1), max_score, findings




# ---------------------------------------------------------------------------
# Tips engine
# ---------------------------------------------------------------------------

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


# ---------------------------------------------------------------------------
# Main analysis
# ---------------------------------------------------------------------------

def analyze_resume(text, num_pages, file_ext):
    text_lower = text.lower()

    checks = [
        ("Contact Information", lambda: check_contact_info(text, text_lower)),
        ("Resume Sections", lambda: check_sections(text_lower)),
        ("Work Experience", lambda: check_work_experience(text, text_lower)),
        ("Education", lambda: check_education(text, text_lower)),
        ("Formatting & Structure", lambda: check_formatting(text, num_pages)),
        ("ATS Compatibility", lambda: check_ats_compatibility(text, file_ext)),
        ("Action Verbs", lambda: check_action_verbs(text_lower)),
        ("Measurable Results", lambda: check_measurable_results(text, text_lower)),
        ("Hard Skills", lambda: check_hard_skills(text_lower)),
        ("Readability", lambda: check_readability(text)),
        ("Writing Consistency", lambda: check_consistency(text)),
        ("Keyword Optimization", lambda: check_keyword_optimization(text_lower)),
    ]

    total_score = 0
    total_max = 0
    categories = []

    for name, fn in checks:
        s, m, findings = fn()
        total_score += s
        total_max += m
        pct = round((s / m) * 100) if m else 0
        categories.append({
            "name": name,
            "score": round(s, 1),
            "max_score": m,
            "percentage": pct,
            "findings": findings,
        })

    overall = round((total_score / total_max) * 100) if total_max else 0

    if overall >= 85:
        verdict = "Excellent! Your resume is highly optimized for ATS systems. Fine-tune with the tips below to reach perfection."
    elif overall >= 70:
        verdict = "Good resume! You're above average, but several improvements could significantly boost your ATS pass rate."
    elif overall >= 55:
        verdict = "Decent foundation, but needs work. Follow the priority tips below to improve your chances significantly."
    elif overall >= 40:
        verdict = "Below average ATS compatibility. Multiple critical areas need attention — focus on the high-priority tips first."
    else:
        verdict = "Significant improvements needed. Your resume will likely be filtered out by most ATS systems. Start with the top recommendations."

    tips = generate_tips(categories, overall, text_lower)

    # Summary stats
    total_findings = sum(len(c["findings"]) for c in categories)
    pass_count = sum(1 for c in categories for f in c["findings"] if f["type"] == "pass")
    fail_count = sum(1 for c in categories for f in c["findings"] if f["type"] == "fail")
    warn_count = sum(1 for c in categories for f in c["findings"] if f["type"] == "warning")

    return {
        "overall_score": overall,
        "verdict": verdict,
        "categories": categories,
        "tips": tips,
        "summary_stats": {
            "total_checks": total_findings,
            "passed": pass_count,
            "warnings": warn_count,
            "failed": fail_count,
        },
        "score_breakdown": {
            "total_earned": round(total_score, 1),
            "total_possible": total_max,
        }
    }


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/robots.txt")
def robots():
    content = "User-agent: *\nAllow: /\nSitemap: " + request.url_root.rstrip("/") + "/sitemap.xml\n"
    return Response(content, mimetype="text/plain")


@app.route("/sitemap.xml")
def sitemap():
    base = request.url_root.rstrip("/")
    xml = '<?xml version="1.0" encoding="UTF-8"?>\n'
    xml += '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    xml += f"  <url><loc>{base}/</loc><changefreq>weekly</changefreq><priority>1.0</priority></url>\n"
    xml += "</urlset>\n"
    return Response(xml, mimetype="application/xml")


@app.route("/api/check", methods=["POST"])
def check_resume():
    if "resume" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files["resume"]
    if file.filename == "":
        return jsonify({"error": "No file selected"}), 400

    if not allowed_file(file.filename):
        return jsonify({"error": "Only PDF and DOCX files are supported"}), 400

    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
    file.save(filepath)

    try:
        file_ext = filename.rsplit(".", 1)[1].lower()
        text, num_pages = extract_text(filepath)
        if not text.strip():
            return jsonify({"error": "Could not extract text. The file may be image-based — use a text-based resume."}), 400
        result = analyze_resume(text, num_pages, file_ext)
        result["file_type"] = file_ext.upper()
        result["word_count"] = len(text.split())
        result["page_count"] = num_pages
    finally:
        os.remove(filepath)

    return jsonify(result)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    debug = os.environ.get("FLASK_ENV") != "production"
    app.run(debug=debug, host="0.0.0.0", port=port)
