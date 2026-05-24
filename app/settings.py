from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True, slots=True)
class AppSettings:
    base_dir: Path
    templates_dir: Path
    static_dir: Path
    secret_key: str
    pdflatex_bin: str
    max_content_length: int

    @classmethod
    def from_env(cls) -> "AppSettings":
        base_dir = Path(__file__).resolve().parent.parent

        return cls(
            base_dir=base_dir,
            templates_dir=base_dir / "templates",
            static_dir=base_dir / "static",
            secret_key=os.getenv("LETTER_APP_SECRET_KEY", "dev-only-change-me"),
            pdflatex_bin=os.getenv("LETTER_APP_PDFLATEX_BIN", "pdflatex"),
            max_content_length=int(os.getenv("LETTER_APP_MAX_CONTENT_LENGTH", "262144")),
        )
