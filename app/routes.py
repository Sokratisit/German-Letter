from __future__ import annotations

import json
import logging
from datetime import date
from io import BytesIO

from flask import (
    Blueprint,
    current_app,
    render_template,
    request,
    send_file,
)

from .latex import LatexBuildError, PandocConversionError, render_letter_pdf
from .validation import normalize_form_input, validate_letter_form

bp = Blueprint("main", __name__)
logger = logging.getLogger(__name__)
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
    "sender_custom_1_key",
    "sender_custom_1_value",
    "sender_custom_2_key",
    "sender_custom_2_value",
    "sender_custom_3_key",
    "sender_custom_3_value",
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
QUERY_PARAM_MAP = {
    "from_name_last": "sender_last_name",
    "from_name_first": "sender_first_name",
    "from_name_title": "sender_title",
    "fromaddress_extra": "sender_extra",
    "fromaddress_street": "sender_street",
    "fromaddress_number": "sender_street_number",
    "fromaddress_postalcode": "sender_postal_code",
    "fromaddress_city": "sender_city",
    "fromcustom1key": "sender_custom_1_key",
    "fromcustom1value": "sender_custom_1_value",
    "fromcustom2key": "sender_custom_2_key",
    "fromcustom2value": "sender_custom_2_value",
    "fromcustom3key": "sender_custom_3_key",
    "fromcustom3value": "sender_custom_3_value",
    "fromphone": "sender_phone",
    "frommobilephone": "sender_mobile_phone",
    "fromfax": "sender_fax",
    "fromemail": "sender_email",
    "fromurl": "sender_url",
    "frombank": "sender_bank",
    "fromlogo": "sender_logo",
    "backaddressseparator": "sender_backaddress_separator",
    "myref": "my_reference",
    "signature": "signature",
    "to_name_last": "recipient_last_name",
    "to_name_first": "recipient_first_name",
    "to_name_title": "recipient_title",
    "toaddress_extra": "recipient_extra",
    "toaddress_street": "recipient_street",
    "toaddress_number": "recipient_street_number",
    "toaddress_postalcode": "recipient_postal_code",
    "toaddress_city": "recipient_city",
    "yourref": "your_reference",
    "yourmail": "your_mail",
    "customer": "customer",
    "invoice": "invoice",
    "title": "letter_title",
    "subject": "subject",
    "subjectseparator": "subject_separator",
    "opening": "opening",
    "body": "body",
    "closing": "closing",
    "ps": "ps",
    "cc": "cc",
    "ccseparator": "cc_separator",
    "encl": "encl",
    "enclseparator": "encl_separator",
    "place": "place",
    "placeseparator": "place_separator",
    "date": "date_iso",
    "filenameaddressee": "filename_addressee",
}


@bp.get("/")
def index() -> str:
    logger.debug("index called")
    form_data = _form_data_from_cookies()
    form_data.update(_form_data_from_query())
    return render_template(
        "index.html",
        errors={},
        form_data=form_data,
        success_message=request.args.get("success", ""),
        today_iso=date.today().isoformat(),
    )


@bp.get("/bedingungen")
def terms() -> str:
    logger.debug("terms called")
    return render_template("terms.html")


@bp.get("/anleitung")
def guide() -> str:
    logger.debug("guide called")
    return render_template("guide.html")


@bp.get("/anleitung-markdown")
def markdown_guide() -> str:
    logger.debug("markdown_guide called")
    return render_template("markdown_guide.html")


@bp.get("/faq")
def faq() -> str:
    logger.debug("faq called")
    return render_template("faq.html")


@bp.post("/generate")
def generate() -> tuple[str, int] | str:
    logger.debug("generate called")
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
            pandoc_bin=current_app.config["PANDOC_BIN"],
            use_docker=current_app.config["LATEX_USE_DOCKER"],
            docker_bin=current_app.config["DOCKER_BIN"],
            docker_image=current_app.config["DOCKER_IMAGE"],
            timeout_seconds=current_app.config["LATEX_TIMEOUT_SECONDS"],
        )
    except (LatexBuildError, PandocConversionError) as exc:
        logger.error("Letter generation exception: %s", exc)
        current_app.logger.exception("Letter generation failed")
        error_message = str(exc)
        if current_app.config.get("LATEX_USE_DOCKER") and isinstance(exc, LatexBuildError):
            error_message = f"{error_message} Hinweis: Docker-Umgebung und Docker-Image-Konfiguration prüfen."
        response = current_app.make_response(
            render_template(
                "index.html",
                errors={"__all__": error_message},
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


def _form_data_from_cookies() -> dict[str, str]:
    logger.debug("_form_data_from_cookies called")
    form_data = {"closing": DEFAULT_CLOSING, "body_mode": "markdown"}
    form_data.update(_load_cookie_data(SENDER_COOKIE_NAME, SENDER_FIELDS))
    form_data.update(_load_cookie_data(RECIPIENT_COOKIE_NAME, RECIPIENT_FIELDS))
    form_data["save_sender"] = "on" if request.cookies.get(SENDER_COOKIE_NAME) else ""
    form_data["save_recipient"] = "on" if request.cookies.get(RECIPIENT_COOKIE_NAME) else ""
    return form_data


def _form_data_from_query() -> dict[str, str]:
    logger.debug("_form_data_from_query called")
    query_data: dict[str, str] = {}
    for query_key, form_key in QUERY_PARAM_MAP.items():
        value = request.args.get(query_key)
        if value is not None:
            query_data[form_key] = value
    return query_data


def _load_cookie_data(cookie_name: str, allowed_fields: tuple[str, ...]) -> dict[str, str]:
    logger.debug("_load_cookie_data called; cookie_name=%s", cookie_name)
    raw_value = request.cookies.get(cookie_name)
    if not raw_value:
        return {}

    try:
        parsed = json.loads(raw_value)
    except json.JSONDecodeError:
        logger.error("Invalid JSON in cookie: %s", cookie_name)
        return {}

    if not isinstance(parsed, dict):
        return {}

    return {field: parsed.get(field, "") for field in allowed_fields if isinstance(parsed.get(field, ""), str)}


def _apply_section_cookies(response, form_data: dict[str, str]) -> None:
    logger.debug("_apply_section_cookies called")
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
    logger.debug("_apply_cookie called; cookie_name=%s should_store=%s", cookie_name, should_store)
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
