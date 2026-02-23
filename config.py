import os

IS_VERCEL = os.environ.get("VERCEL") or os.environ.get("AWS_LAMBDA_FUNCTION_NAME")
UPLOAD_DIR = "/tmp/uploads" if IS_VERCEL else os.path.join(os.path.dirname(__file__), "uploads")
MAX_CONTENT_LENGTH = 5 * 1024 * 1024
ALLOWED_EXTENSIONS = {"pdf", "docx"}
