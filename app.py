from __future__ import annotations

import argparse
import os
import traceback

from flask import Flask, jsonify
from chatbot_app import bootstrap_app_state, create_app


def build_bootstrap_error_app(exc: Exception) -> Flask:
    fallback = Flask(__name__)
    expose_detail = os.getenv("VERCEL_ENV", "").lower() not in {"", "production"}
    payload = {"error": "Application bootstrap failed during startup."}
    if expose_detail:
        payload["detail"] = str(exc)

    @fallback.route("/", defaults={"path": ""}, methods=["GET", "POST", "PATCH", "DELETE", "OPTIONS", "HEAD"])
    @fallback.route("/<path:path>", methods=["GET", "POST", "PATCH", "DELETE", "OPTIONS", "HEAD"])
    def startup_error(path: str = ""):
        return jsonify(payload), 500

    return fallback


app = build_bootstrap_error_app(RuntimeError("Application bootstrap has not completed yet."))


try:
    app = create_app()
except Exception as exc:  # pragma: no cover - only exercised when app bootstrap fails
    traceback.print_exc()
    app = build_bootstrap_error_app(exc)


def main() -> None:
    parser = argparse.ArgumentParser(description="College query chatbot")
    parser.add_argument(
        "command",
        nargs="?",
        default="runserver",
        choices=["runserver", "bootstrap"],
        help="Run the web server or bootstrap the database",
    )
    parser.add_argument("--host", default="127.0.0.1", help="Host for the development server")
    parser.add_argument("--port", default=5000, type=int, help="Port for the development server")
    parser.add_argument("--debug", action="store_true", help="Enable Flask debug mode")
    args = parser.parse_args()

    if args.command == "bootstrap":
        with app.app_context():
            bootstrap_app_state()
        print("Database, admin user, starter FAQs, and sample knowledge are ready.")
        return

    app.run(host=args.host, port=args.port, debug=args.debug)


if __name__ == "__main__":
    main()
