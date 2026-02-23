SECTION_KEYWORDS = {
    "contact": ["email", "phone", "address", "linkedin", "github", "portfolio", "website", "contact"],
    "summary": ["summary", "objective", "professional summary",
                 "career objective", "career summary", "professional profile", "executive summary"],
    "experience": ["work experience", "professional experience",
                    "work history", "employment history", "relevant experience"],
    "education": ["education", "academic background", "educational background"],
    "skills": ["skills", "technical skills", "competencies", "proficiencies",
               "core competencies", "areas of expertise", "key skills"],
    "certifications": ["certifications", "certificates", "professional certifications"],
    "projects": ["projects", "personal projects", "academic projects", "key projects"],
    "awards": ["awards", "honors", "achievements"],
    "languages": ["languages", "language proficiency"],
    "volunteer": ["volunteer", "volunteering", "community service"],
    "references": ["references"],
    "publications": ["publications", "research papers"],
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
