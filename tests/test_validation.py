from datetime import date

from app.validation import validate_letter_form


def _valid_payload() -> dict[str, str]:
    return {
        "sender_last_name": "Mustermann",
        "sender_first_name": "Max",
        "sender_title": "Dr.",
        "sender_extra": "2. Etage",
        "sender_street": "Musterweg",
        "sender_street_number": "1",
        "sender_postal_code": "12345",
        "sender_city": "Berlin",
        "sender_phone": "030 123456",
        "sender_mobile_phone": "0171 2345678",
        "sender_fax": "030 654321",
        "sender_email": "max@example.com",
        "sender_url": "https://example.com",
        "sender_bank": "IBAN DE21 87654321 13456789",
        "sender_logo": "",
        "sender_backaddress_separator": ", ",
        "my_reference": "MM-2026-04",
        "signature": "Dr. Max Mustermann",
        "recipient_last_name": "Beispiel",
        "recipient_first_name": "Erika",
        "recipient_title": "",
        "recipient_extra": "Personalabteilung",
        "recipient_street": "Firmenstraße",
        "recipient_street_number": "4",
        "recipient_postal_code": "98765",
        "recipient_city": "Hamburg",
        "your_reference": "BG-77",
        "your_mail": "01.04.2026",
        "customer": "4711",
        "invoice": "R-99",
        "letter_title": "Mahnung",
        "subject": "Kündigung",
        "subject_separator": ": ",
        "opening": "Sehr geehrte Frau Beispiel,",
        "body_mode": "markdown",
        "body": "Hiermit kündige ich den Vertrag fristgerecht.",
        "closing": "Mit freundlichen Grüßen",
        "ps": "Bitte bestätigen Sie den Eingang.",
        "cc": "Ablage",
        "cc_separator": "Verteiler",
        "encl": "Vertrag",
        "encl_separator": "Anlagen",
        "place": "Berlin",
        "place_separator": ", ",
        "date_iso": "24.04.2026",
        "filename_addressee": "Beispiel",
    }


def test_validation_accepts_valid_payload() -> None:
    data, errors = validate_letter_form(_valid_payload())
    assert data is not None
    assert errors == {}
    assert data.date_iso == date(2026, 4, 24)
    assert data.filename_addressee == "Beispiel"
    assert data.sender_display_name == "Dr. Max Mustermann"
    assert data.body_mode == "markdown"
    assert data.body == "Hiermit kündige ich den Vertrag fristgerecht."


def test_validation_allows_empty_optional_content_fields() -> None:
    payload = _valid_payload()
    payload["subject"] = ""
    payload["your_mail"] = ""
    payload["cc"] = ""
    payload["date_iso"] = ""
    data, errors = validate_letter_form(payload)
    assert data is not None
    assert errors == {}
    assert data.subject == ""
    assert data.your_mail == ""
    assert data.cc == ""
    assert data.date_iso is None


def test_validation_rejects_invalid_date() -> None:
    payload = _valid_payload()
    payload["date_iso"] = "2026/04/24"
    data, errors = validate_letter_form(payload)
    assert data is None
    assert errors["date_iso"] == "Datum muss im Format TT.MM.JJJJ sein."


def test_validation_accepts_single_digit_day_and_month() -> None:
    payload = _valid_payload()
    payload["date_iso"] = "1.3.2004"
    data, errors = validate_letter_form(payload)
    assert errors == {}
    assert data is not None
    assert data.date_iso == date(2004, 3, 1)


def test_validation_accepts_iso_date_too() -> None:
    payload = _valid_payload()
    payload["date_iso"] = "2004-03-01"
    data, errors = validate_letter_form(payload)
    assert errors == {}
    assert data is not None
    assert data.date_iso == date(2004, 3, 1)
