from __future__ import annotations

import argparse

from chatbot_app import bootstrap_app_state, create_app


app = create_app()


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

