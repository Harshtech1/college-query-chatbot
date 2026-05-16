from __future__ import annotations

from pathlib import Path

from dotenv import load_dotenv
from flask import Flask

from chatbot_app.config import Config
from chatbot_app.database import db


def create_app(test_config: dict | None = None) -> Flask:
    load_dotenv()
    root_dir = Path(__file__).resolve().parent.parent
    public_dir = root_dir / "public"
    app = Flask(
        __name__,
        template_folder=str(root_dir / "templates"),
        static_folder=str(public_dir),
        static_url_path="",
        instance_path=str(Config.INSTANCE_DIR),
        instance_relative_config=False,
    )
    app.config.from_object(Config)

    if test_config:
        app.config.update(test_config)

    Path(app.instance_path).mkdir(parents=True, exist_ok=True)
    Path(app.static_folder).mkdir(parents=True, exist_ok=True)
    Path(app.config["UPLOAD_DIR"]).mkdir(parents=True, exist_ok=True)

    db.init_app(app)

    from chatbot_app.routes.admin import admin_bp
    from chatbot_app.routes.api import api_bp
    from chatbot_app.routes.main import main_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(api_bp)

    with app.app_context():
        bootstrap_app_state()

    @app.context_processor
    def inject_globals() -> dict:
        return {
            "app_name": "Academic Service Interface",
            "institution_name": "University Name",
            "institution_office": "Office of Academic Affairs & Student Services",
            "service_name": "Student Query Desk",
            "admin_enabled": app.config["ADMIN_ENABLED"],
            "demo_mode": app.config["DEMO_MODE"],
            "is_vercel": app.config["IS_VERCEL"],
        }

    return app


def bootstrap_app_state() -> None:
    from chatbot_app.seed import seed_defaults

    db.create_all()
    seed_defaults()
