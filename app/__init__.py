from __future__ import annotations

from .settings import AppSettings


def create_app(settings: AppSettings | None = None):
    from flask import Flask
    from .routes import bp

    app_settings = settings or AppSettings.from_env()

    app = Flask(
        __name__,
        template_folder=str(app_settings.templates_dir),
        static_folder=str(app_settings.static_dir),
    )
    app.config.from_mapping(
        SECRET_KEY=app_settings.secret_key,
        PDFLATEX_BIN=app_settings.pdflatex_bin,
        MAX_CONTENT_LENGTH=app_settings.max_content_length,
    )

    app.register_blueprint(bp)
    return app
