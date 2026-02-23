import os
from flask import Flask
from config import UPLOAD_DIR, MAX_CONTENT_LENGTH
from routes import bp


def create_app():
    app = Flask(__name__)
    app.config["MAX_CONTENT_LENGTH"] = MAX_CONTENT_LENGTH
    app.config["UPLOAD_FOLDER"] = UPLOAD_DIR
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    app.register_blueprint(bp)
    return app


app = create_app()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    debug = os.environ.get("FLASK_ENV") != "production"
    app.run(debug=debug, host="0.0.0.0", port=port)
