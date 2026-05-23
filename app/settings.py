from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True, slots=True)
class AppSettings:
    base_dir: Path
    templates_dir: Path
    static_dir: Path
    generated_dir: Path
    secret_key: str
    pdflatex_bin: str
    max_content_length: int

    @classmethod
    def from_env(cls) -> "AppSettings":
        base_dir = Path(__file__).resolve().parent.parent
        generated_dir_raw = os.getenv("LETTER_APP_GENERATED_DIR")
        generated_dir = (
            Path(generated_dir_raw).expanduser().resolve()
            if generated_dir_raw
            else Path(r"D:\Users\Admin\Documents\Letter")
        )

        return cls(
            base_dir=base_dir,
            templates_dir=base_dir / "templates",
            static_dir=base_dir / "static",
            generated_dir=generated_dir,
            secret_key=os.getenv("LETTER_APP_SECRET_KEY", "dev-only-change-me"),
            pdflatex_bin=os.getenv("LETTER_APP_PDFLATEX_BIN", "pdflatex"),
            max_content_length=int(os.getenv("LETTER_APP_MAX_CONTENT_LENGTH", "262144")),
        )
