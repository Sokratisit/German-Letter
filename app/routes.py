from __future__ import annotations

import os
from datetime import date
from pathlib import Path

from flask import (
    Blueprint,
    abort,
    current_app,
    redirect,
    render_template,
    request,
    send_from_directory,
    url_for,
)

from .latex import LatexBuildError, generate_letter_pdf
from .validation import normalize_form_input, validate_letter_form

bp = Blueprint("main", __name__)
DEFAULT_CLOSING = "Mit freundlichen Grüßen"


@bp.get("/")
def index() -> str:
    return render_template(
        "index.html",
        errors={},
        form_data={"closing": DEFAULT_CLOSING},
        success_message=request.args.get("success", ""),
        today_iso=date.today().isoformat(),
    )


@bp.post("/generate")
def generate() -> tuple[str, int] | str:
    form_data = normalize_form_input(dict(request.form.items()))
    validated, errors = validate_letter_form(form_data)
    if errors:
        return (
            render_template(
                "index.html",
                errors=errors,
                form_data=form_data,
                success_message="",
                today_iso=form_data.get("date_iso", date.today().isoformat()),
            ),
            400,
        )

    try:
        pdf_path = generate_letter_pdf(
            validated,
            generated_dir=Path(current_app.config["GENERATED_DIR"]),
            pdflatex_bin=current_app.config["PDFLATEX_BIN"],
        )
    except LatexBuildError as exc:
        current_app.logger.exception("Letter generation failed")
        return (
            render_template(
                "index.html",
                errors={"__all__": str(exc)},
                form_data=form_data,
                success_message="",
                today_iso=form_data.get("date_iso", date.today().isoformat()),
            ),
            500,
        )

    _open_with_default_app(pdf_path)
    return redirect(
        url_for(
            "main.index",
            success=f"Der Brief wurde erstellt: {pdf_path.name}",
        )
    )


@bp.get("/generated/<path:filename>")
def download_generated(filename: str):
    safe_name = Path(filename).name
    if safe_name != filename or not safe_name.endswith(".pdf"):
        abort(404)

    return send_from_directory(
        current_app.config["GENERATED_DIR"],
        safe_name,
        as_attachment=True,
        download_name=safe_name,
    )


def _open_with_default_app(path: Path) -> None:
    try:
        os.startfile(path)  # type: ignore[attr-defined]
    except OSError:
        current_app.logger.exception("Opening generated PDF failed")
