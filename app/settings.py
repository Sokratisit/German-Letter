from __future__ import annotations

import logging
import os
from dataclasses import dataclass
from pathlib import Path
logger = logging.getLogger(__name__)


@dataclass(frozen=True, slots=True)
class AppSettings:
    base_dir: Path
    templates_dir: Path
    static_dir: Path
    secret_key: str
    latex_bin: str
    latex_font_family: str
    pandoc_bin: str
    latex_use_docker: bool
    docker_image: str
    docker_bin: str
    latex_timeout_seconds: int
    max_content_length: int

    @classmethod
    def from_env(cls) -> "AppSettings":
        logger.debug("AppSettings.from_env called")
        base_dir = Path(__file__).resolve().parent.parent

        return cls(
            base_dir=base_dir,
            templates_dir=base_dir / "templates",
            static_dir=base_dir / "static",
            secret_key=os.getenv("LETTER_APP_SECRET_KEY", "dev-only-change-me"),
            latex_bin=os.getenv("LETTER_APP_LATEX_BIN") or os.getenv("LETTER_APP_PDFLATEX_BIN", "lualatex"),
            latex_font_family=os.getenv("LETTER_APP_LATEX_FONT_FAMILY", "TeX Gyre Heros"),
            pandoc_bin=os.getenv("LETTER_APP_PANDOC_BIN", "pandoc"),
            latex_use_docker=os.getenv("LETTER_APP_LATEX_USE_DOCKER", "true").lower() == "true",
            docker_image=os.getenv("LETTER_APP_DOCKER_IMAGE", "blang/latex:ctanfull"),
            docker_bin=os.getenv("LETTER_APP_DOCKER_BIN", "docker"),
            latex_timeout_seconds=int(os.getenv("LETTER_APP_LATEX_TIMEOUT_SECONDS", "20")),
            max_content_length=int(os.getenv("LETTER_APP_MAX_CONTENT_LENGTH", "262144")),
        )
