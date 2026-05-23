from __future__ import annotations

import json
from datetime import date
from io import BytesIO
from pathlib import Path

from flask import (
    Blueprint,
    abort,
    current_app,
    render_template,
    request,
    send_file,
    send_from_directory,
)

from .latex import LatexBuildError, render_letter_pdf
from .validation import normalize_form_input, validate_letter_form

bp = Blueprint("main", __name__)
DEFAULT_CLOSING = "Mit freundlichen Grüßen"
SENDER_COOKIE_NAME = "letter_sender"
RECIPIENT_COOKIE_NAME = "letter_recipient"
SENDER_FIELDS = (
    "sender_last_name",
    "sender_first_name",
    "sender_title",
    "sender_extra",
    "sender_street",
    "sender_street_number",
    "sender_postal_code",
    "sender_city",
    "sender_phone",
    "sender_mobile_phone",
    "sender_fax",
    "sender_email",
    "sender_url",
    "sender_bank",
    "sender_logo",
    "sender_backaddress_separator",
    "my_reference",
    "signature",
)
RECIPIENT_FIELDS = (
    "recipient_last_name",
    "recipient_first_name",
    "recipient_title",
    "recipient_extra",
    "recipient_street",
    "recipient_street_number",
    "recipient_postal_code",
    "recipient_city",
    "your_reference",
    "your_mail",
    "customer",
    "invoice",
)


@bp.get("/")
def index() -> str:
    form_data = _form_data_from_cookies()
    return render_template(
        "index.html",
        errors={},
        form_data=form_data,
        success_message=request.args.get("success", ""),
        today_iso=date.today().isoformat(),
    )


@bp.post("/generate")
def generate() -> tuple[str, int] | str:
    form_data = normalize_form_input(dict(request.form.items()))
    validated, errors = validate_letter_form(form_data)
    if errors:
        response = current_app.make_response(
            render_template(
                "index.html",
                errors=errors,
                form_data=form_data,
                success_message="",
                today_iso=form_data.get("date_iso", date.today().isoformat()),
            )
        )
        response.status_code = 400
        _apply_section_cookies(response, form_data)
        return response

    try:
        filename, pdf_bytes = render_letter_pdf(
            validated,
            pdflatex_bin=current_app.config["PDFLATEX_BIN"],
        )
    except LatexBuildError as exc:
        current_app.logger.exception("Letter generation failed")
        response = current_app.make_response(
            render_template(
                "index.html",
                errors={"__all__": str(exc)},
                form_data=form_data,
                success_message="",
                today_iso=form_data.get("date_iso", date.today().isoformat()),
            )
        )
        response.status_code = 500
        _apply_section_cookies(response, form_data)
        return response

    response = send_file(
        BytesIO(pdf_bytes),
        mimetype="application/pdf",
        as_attachment=True,
        download_name=filename,
    )
    _apply_section_cookies(response, form_data)
    return response


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


def _form_data_from_cookies() -> dict[str, str]:
    form_data = {"closing": DEFAULT_CLOSING}
    form_data.update(_load_cookie_data(SENDER_COOKIE_NAME, SENDER_FIELDS))
    form_data.update(_load_cookie_data(RECIPIENT_COOKIE_NAME, RECIPIENT_FIELDS))
    form_data["save_sender"] = "on" if request.cookies.get(SENDER_COOKIE_NAME) else ""
    form_data["save_recipient"] = "on" if request.cookies.get(RECIPIENT_COOKIE_NAME) else ""
    return form_data


def _load_cookie_data(cookie_name: str, allowed_fields: tuple[str, ...]) -> dict[str, str]:
    raw_value = request.cookies.get(cookie_name)
    if not raw_value:
        return {}

    try:
        parsed = json.loads(raw_value)
    except json.JSONDecodeError:
        return {}

    if not isinstance(parsed, dict):
        return {}

    return {field: parsed.get(field, "") for field in allowed_fields if isinstance(parsed.get(field, ""), str)}


def _apply_section_cookies(response, form_data: dict[str, str]) -> None:
    _apply_cookie(
        response,
        cookie_name=SENDER_COOKIE_NAME,
        should_store=bool(form_data.get("save_sender")),
        field_names=SENDER_FIELDS,
        form_data=form_data,
    )
    _apply_cookie(
        response,
        cookie_name=RECIPIENT_COOKIE_NAME,
        should_store=bool(form_data.get("save_recipient")),
        field_names=RECIPIENT_FIELDS,
        form_data=form_data,
    )


def _apply_cookie(response, *, cookie_name: str, should_store: bool, field_names: tuple[str, ...], form_data: dict[str, str]) -> None:
    if not should_store:
        response.delete_cookie(cookie_name)
        return

    cookie_value = json.dumps({field: form_data.get(field, "") for field in field_names}, ensure_ascii=False, separators=(",", ":"))
    response.set_cookie(
        cookie_name,
        cookie_value,
        max_age=60 * 60 * 24 * 365,
        samesite="Lax",
    )
