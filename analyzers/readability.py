import re


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

    paragraphs = text.split("\n\n")
    long_paras = sum(1 for p in paragraphs if len(p.split()) > 60)
    if long_paras == 0:
        score += 1.5
        findings.append({"type": "pass", "message": "Good content density — no large text blocks that overwhelm readers"})
    else:
        score += 0.5
        findings.append({"type": "warning", "message": f"{long_paras} dense paragraph(s) found — break into bullet points for better readability"})

    return round(min(score, max_score), 1), max_score, findings
