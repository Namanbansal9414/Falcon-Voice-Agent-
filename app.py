# app.py
from flask import Flask, send_from_directory
from routes.voice import bp as voice_bp


def create_app():
    app = Flask(
        __name__,
        static_folder="static",
        static_url_path="/static",
    )

    app.register_blueprint(voice_bp)

    @app.route("/")
    def index():
        return send_from_directory("static", "index.html")

    @app.get("/health")
    def health():
        return {"status": "ok"}

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=5000, debug=True)
