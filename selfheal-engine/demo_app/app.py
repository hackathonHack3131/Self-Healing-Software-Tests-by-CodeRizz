"""Flask demo shop application featuring four checkout versions."""

import os
from flask import Flask, jsonify, redirect, render_template, request, session, url_for
from demo_app.data import ORDER_ID, TOTAL, WRONG_TOTAL, get_cart_data


def create_app() -> Flask:
    """Create and configure the Flask application."""
    app = Flask(
        __name__,
        template_folder="templates",
        static_folder="static",
    )
    app.secret_key = os.getenv("SECRET_KEY", "selfheal-demo-secret-key-3650")

    @app.route("/")
    def index():
        return render_template("index.html", css_file="a.css", version="")

    @app.route("/health")
    def health():
        return jsonify({"status": "ok", "app": "selfheal-shop"}), 200

    # -------------------------------------------------------------
    # Version A: Single-page checkout
    # -------------------------------------------------------------
    @app.route("/v/a/")
    def version_a_checkout():
        return render_template(
            "a/checkout.html",
            cart=get_cart_data(),
            css_file="a.css",
            version="a",
        )

    @app.route("/v/a/place", methods=["GET", "POST"])
    def version_a_place():
        if request.method == "POST":
            session["order_a"] = {
                "name": request.form.get("name"),
                "email": request.form.get("email"),
                "address": request.form.get("address"),
                "card_number": request.form.get("card_number"),
                "expiry": request.form.get("expiry"),
                "cvc": request.form.get("cvc"),
            }
        return redirect(url_for("version_a_confirmation"))

    @app.route("/v/a/confirmation", methods=["GET", "POST"])
    def version_a_confirmation():
        return render_template(
            "a/confirmation.html",
            order_id=ORDER_ID,
            total=f"{TOTAL:.2f}",
            css_file="a.css",
            version="a",
        )

    # -------------------------------------------------------------
    # Versions B, C, D: Multi-step checkout
    # -------------------------------------------------------------
    @app.route("/v/<version>/")
    def multi_step_cart(version):
        if version not in ("b", "c", "d"):
            return redirect(url_for("index"))
        if f"checkout_{version}" not in session:
            session[f"checkout_{version}"] = {}
        return render_template(
            "b/cart.html",
            cart=get_cart_data(),
            css_file="b.css",
            version=version,
        )

    @app.route("/v/<version>/shipping", methods=["GET", "POST"])
    def multi_step_shipping(version):
        if version not in ("b", "c", "d"):
            return redirect(url_for("index"))

        session_key = f"checkout_{version}"
        current_data = session.get(session_key, {})

        if request.method == "POST":
            current_data.update(
                {
                    "full_name": request.form.get("full_name", ""),
                    "email_address": request.form.get("email_address", ""),
                    "street_address": request.form.get("street_address", ""),
                }
            )
            session[session_key] = current_data
            return redirect(url_for("multi_step_payment", version=version))

        return render_template(
            "b/shipping.html",
            session_data=current_data,
            css_file="b.css",
            version=version,
        )

    @app.route("/v/<version>/payment", methods=["GET", "POST"])
    def multi_step_payment(version):
        if version not in ("b", "c", "d"):
            return redirect(url_for("index"))

        session_key = f"checkout_{version}"
        current_data = session.get(session_key, {})

        if request.method == "POST":
            current_data.update(
                {
                    "card_number": request.form.get("card_number", ""),
                    "expiry": request.form.get("expiry", ""),
                    "cvc": request.form.get("cvc", ""),
                }
            )
            session[session_key] = current_data
            return redirect(url_for("multi_step_review", version=version))

        return render_template(
            "b/payment.html",
            session_data=current_data,
            css_file="b.css",
            version=version,
        )

    @app.route("/v/<version>/review", methods=["GET", "POST"])
    def multi_step_review(version):
        if version not in ("b", "c", "d"):
            return redirect(url_for("index"))

        session_key = f"checkout_{version}"
        current_data = session.get(session_key, {})
        return render_template(
            "b/review.html",
            cart=get_cart_data(),
            session_data=current_data,
            css_file="b.css",
            version=version,
        )

    @app.route("/v/<version>/place", methods=["GET", "POST"])
    def multi_step_place(version):
        if version not in ("b", "c", "d"):
            return redirect(url_for("index"))

        if version == "c":
            # Version C failure mode: Payment gateway error (HTTP 500)
            return (
                render_template(
                    "b/error.html",
                    css_file="b.css",
                    version="c",
                ),
                500,
            )

        return redirect(url_for("multi_step_confirmation", version=version))

    @app.route("/v/<version>/confirmation", methods=["GET", "POST"])
    def multi_step_confirmation(version):
        if version not in ("b", "d"):
            return redirect(url_for("index"))

        # Version D has a math/total calculation bug (shows 32.50 instead of 36.50)
        display_total = f"{WRONG_TOTAL:.2f}" if version == "d" else f"{TOTAL:.2f}"

        return render_template(
            "b/confirmation.html",
            order_id=ORDER_ID,
            total=display_total,
            css_file="b.css",
            version=version,
        )

    return app


if __name__ == "__main__":
    app = create_app()
    host = os.getenv("HOST", "127.0.0.1")
    port = int(os.getenv("PORT", "5000"))
    app.run(host=host, port=port, debug=False)
