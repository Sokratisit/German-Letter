from __future__ import annotations

import logging
from .settings import AppSettings
logger = logging.getLogger(__name__)


def create_app(settings: AppSettings | None = None):
    logger.debug("create_app called")
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
        PANDOC_BIN=app_settings.pandoc_bin,
        LATEX_USE_DOCKER=app_settings.latex_use_docker,
        DOCKER_IMAGE=app_settings.docker_image,
        DOCKER_BIN=app_settings.docker_bin,
        LATEX_TIMEOUT_SECONDS=app_settings.latex_timeout_seconds,
        MAX_CONTENT_LENGTH=app_settings.max_content_length,
    )

    app.register_blueprint(bp)
    return app
