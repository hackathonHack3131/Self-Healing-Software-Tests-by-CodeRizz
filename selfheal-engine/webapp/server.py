"""SelfHeal Web Application server factory and runner."""

import os
from pathlib import Path
from flask import Flask, redirect, render_template
from webapp.api import api_bp


def create_app() -> Flask:
    """Create and configure the SelfHeal dashboard web application."""
    base_dir = Path(__file__).resolve().parent
    app = Flask(
        __name__,
        template_folder=str(base_dir / "templates"),
        static_folder=str(base_dir / "static"),
    )
    app.secret_key = os.getenv("SECRET_KEY", "selfheal-dashboard-secret-8941")

    # Register API blueprint
    app.register_blueprint(api_bp)

    @app.route("/")
    @app.route("/index.html")
    def home():
        """Serve the Home landing page."""
        return render_template("home.html")

    @app.route("/demo")
    @app.route("/studio")
    def demo():
        """Serve the Interactive Testing Studio & Verification Engine."""
        return render_template("demo.html")

    @app.route("/about")
    def about():
        """Serve the Architecture & About page."""
        return render_template("about.html")

    @app.route("/contact")
    def contact():
        """Serve the Contact & Feedback page."""
        return render_template("contact.html")

    @app.route("/github-intelligence")
    @app.route("/github")
    def github_intelligence():
        """Serve the GitHub Change Intelligence page."""
        return render_template("github_intelligence.html")

    return app



if __name__ == "__main__":
    app = create_app()
    port = int(os.getenv("WEBAPP_PORT", "8080"))
    host = os.getenv("WEBAPP_HOST", "0.0.0.0")
    print(f"Starting SelfHeal Dashboard at http://127.0.0.1:{port}")
    app.run(host=host, port=port, debug=False)
