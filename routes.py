import os
from datetime import date
from flask import Blueprint, request, jsonify, render_template, Response, current_app
from werkzeug.utils import secure_filename
from parsers import allowed_file, extract_text
from analysis import analyze_resume

bp = Blueprint("main", __name__)


@bp.route("/")
def index():
    return render_template("index.html")


@bp.route("/robots.txt")
def robots():
    content = "User-agent: *\nAllow: /\nSitemap: " + request.url_root.rstrip("/") + "/sitemap.xml\n"
    return Response(content, mimetype="text/plain")


@bp.route("/sitemap.xml")
def sitemap():
    base = request.url_root.rstrip("/")
    today = date.today().isoformat()
    xml = '<?xml version="1.0" encoding="UTF-8"?>\n'
    xml += '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    xml += f"  <url>\n    <loc>{base}/</loc>\n    <lastmod>{today}</lastmod>\n    <changefreq>weekly</changefreq>\n    <priority>1.0</priority>\n  </url>\n"
    xml += f"  <url>\n    <loc>{base}/#how-it-works</loc>\n    <lastmod>{today}</lastmod>\n    <changefreq>monthly</changefreq>\n    <priority>0.8</priority>\n  </url>\n"
    xml += f"  <url>\n    <loc>{base}/#faq</loc>\n    <lastmod>{today}</lastmod>\n    <changefreq>monthly</changefreq>\n    <priority>0.7</priority>\n  </url>\n"
    xml += "</urlset>\n"
    return Response(xml, mimetype="application/xml")


@bp.route("/api/check", methods=["POST"])
def check_resume():
    if "resume" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files["resume"]
    if file.filename == "":
        return jsonify({"error": "No file selected"}), 400

    if not allowed_file(file.filename):
        return jsonify({"error": "Only PDF and DOCX files are supported"}), 400

    filename = secure_filename(file.filename)
    filepath = os.path.join(current_app.config["UPLOAD_FOLDER"], filename)
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
