from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Mapping

MAX_LENGTHS: dict[str, int] = {
    "sender_last_name": 120,
    "sender_first_name": 120,
    "sender_title": 120,
    "sender_extra": 120,
    "sender_street": 120,
    "sender_street_number": 30,
    "sender_postal_code": 20,
    "sender_city": 120,
    "sender_custom_1_key": 120,
    "sender_custom_1_value": 300,
    "sender_custom_2_key": 120,
    "sender_custom_2_value": 300,
    "sender_custom_3_key": 120,
    "sender_custom_3_value": 300,
    "sender_phone": 120,
    "sender_mobile_phone": 120,
    "sender_fax": 120,
    "sender_email": 254,
    "sender_url": 300,
    "sender_bank": 800,
    "sender_logo": 500,
    "sender_backaddress_separator": 40,
    "my_reference": 120,
    "signature": 120,
    "recipient_last_name": 120,
    "recipient_first_name": 120,
    "recipient_title": 120,
    "recipient_extra": 120,
    "recipient_street": 120,
    "recipient_street_number": 30,
    "recipient_postal_code": 20,
    "recipient_city": 120,
    "your_reference": 120,
    "your_mail": 120,
    "customer": 120,
    "invoice": 120,
    "letter_title": 180,
    "subject": 180,
    "subject_separator": 80,
    "opening": 180,
    "body": 5000,
    "closing": 120,
    "ps": 500,
    "cc": 800,
    "cc_separator": 80,
    "encl": 800,
    "encl_separator": 80,
    "place": 120,
    "place_separator": 80,
    "filename_addressee": 180,
}


@dataclass(frozen=True, slots=True)
class LetterFormData:
    sender_last_name: str
    sender_first_name: str
    sender_title: str
    sender_extra: str
    sender_street: str
    sender_street_number: str
    sender_postal_code: str
    sender_city: str
    sender_custom_1_key: str
    sender_custom_1_value: str
    sender_custom_2_key: str
    sender_custom_2_value: str
    sender_custom_3_key: str
    sender_custom_3_value: str
    sender_phone: str
    sender_mobile_phone: str
    sender_fax: str
    sender_email: str
    sender_url: str
    sender_bank: str
    sender_logo: str
    sender_backaddress_separator: str
    my_reference: str
    signature: str
    recipient_last_name: str
    recipient_first_name: str
    recipient_title: str
    recipient_extra: str
    recipient_street: str
    recipient_street_number: str
    recipient_postal_code: str
    recipient_city: str
    your_reference: str
    your_mail: str
    customer: str
    invoice: str
    letter_title: str
    subject: str
    subject_separator: str
    opening: str
    body: str
    closing: str
    ps: str
    cc: str
    cc_separator: str
    encl: str
    encl_separator: str
    place: str
    place_separator: str
    date_iso: date | None
    filename_addressee: str

    @property
    def sender_display_name(self) -> str:
        return _join_non_empty((self.sender_title, self.sender_first_name, self.sender_last_name))

    @property
    def recipient_display_name(self) -> str:
        return _join_non_empty(
            (self.recipient_title, self.recipient_first_name, self.recipient_last_name)
        )


def validate_letter_form(
    form: Mapping[str, str], *, today: date | None = None
) -> tuple[LetterFormData | None, dict[str, str]]:
    normalized_form = normalize_form_input(form)
    errors: dict[str, str] = {}
    cleaned: dict[str, str] = {}

    for key, max_length in MAX_LENGTHS.items():
        value = normalized_form.get(key, "")
        cleaned[key] = value
        if value and len(value) > max_length:
            errors[key] = f"{_label_for_field(key)} darf maximal {max_length} Zeichen enthalten."

    date_raw = normalized_form.get("date_iso", "")
    if date_raw:
        try:
            parsed_date = date.fromisoformat(date_raw)
        except ValueError:
            errors["date_iso"] = "Datum muss im Format YYYY-MM-DD sein."
            parsed_date = today or date.today()
    else:
        parsed_date = None

    if errors:
        return None, errors

    return (
        LetterFormData(
            sender_last_name=cleaned["sender_last_name"],
            sender_first_name=cleaned["sender_first_name"],
            sender_title=cleaned["sender_title"],
            sender_extra=cleaned["sender_extra"],
            sender_street=cleaned["sender_street"],
            sender_street_number=cleaned["sender_street_number"],
            sender_postal_code=cleaned["sender_postal_code"],
            sender_city=cleaned["sender_city"],
            sender_custom_1_key=cleaned["sender_custom_1_key"],
            sender_custom_1_value=cleaned["sender_custom_1_value"],
            sender_custom_2_key=cleaned["sender_custom_2_key"],
            sender_custom_2_value=cleaned["sender_custom_2_value"],
            sender_custom_3_key=cleaned["sender_custom_3_key"],
            sender_custom_3_value=cleaned["sender_custom_3_value"],
            sender_phone=cleaned["sender_phone"],
            sender_mobile_phone=cleaned["sender_mobile_phone"],
            sender_fax=cleaned["sender_fax"],
            sender_email=cleaned["sender_email"],
            sender_url=cleaned["sender_url"],
            sender_bank=cleaned["sender_bank"].replace("\r\n", "\n"),
            sender_logo=cleaned["sender_logo"],
            sender_backaddress_separator=cleaned["sender_backaddress_separator"],
            my_reference=cleaned["my_reference"],
            signature=cleaned["signature"],
            recipient_last_name=cleaned["recipient_last_name"],
            recipient_first_name=cleaned["recipient_first_name"],
            recipient_title=cleaned["recipient_title"],
            recipient_extra=cleaned["recipient_extra"],
            recipient_street=cleaned["recipient_street"],
            recipient_street_number=cleaned["recipient_street_number"],
            recipient_postal_code=cleaned["recipient_postal_code"],
            recipient_city=cleaned["recipient_city"],
            your_reference=cleaned["your_reference"],
            your_mail=cleaned["your_mail"],
            customer=cleaned["customer"],
            invoice=cleaned["invoice"],
            letter_title=cleaned["letter_title"],
            subject=cleaned["subject"],
            subject_separator=cleaned["subject_separator"],
            opening=cleaned["opening"],
            body=cleaned["body"].replace("\r\n", "\n"),
            closing=cleaned["closing"],
            ps=cleaned["ps"],
            cc=cleaned["cc"].replace("\r\n", "\n"),
            cc_separator=cleaned["cc_separator"],
            encl=cleaned["encl"].replace("\r\n", "\n"),
            encl_separator=cleaned["encl_separator"],
            place=cleaned["place"],
            place_separator=cleaned["place_separator"],
            date_iso=parsed_date,
            filename_addressee=cleaned["filename_addressee"],
        ),
        {},
    )


def normalize_form_input(form: Mapping[str, str]) -> dict[str, str]:
    formatting_fields = {
        "sender_backaddress_separator",
        "subject_separator",
        "cc_separator",
        "encl_separator",
        "place_separator",
    }
    normalized: dict[str, str] = {}
    for key, value in form.items():
        normalized[key] = value if key == "date_iso" or key in formatting_fields else value.strip()
    return normalized


def _join_non_empty(values: tuple[str, ...]) -> str:
    return " ".join(value for value in values if value)


def _label_for_field(key: str) -> str:
    labels = {
        "sender_last_name": "Absender Nachname",
        "sender_first_name": "Absender Vorname",
        "sender_title": "Absender Titel",
        "sender_extra": "Absender Zusatz",
        "sender_street": "Absender Straße",
        "sender_street_number": "Absender Nummer",
        "sender_postal_code": "Absender PLZ",
        "sender_city": "Absender Ort",
        "sender_custom_1_key": "Absender Zusatzschlüssel 1",
        "sender_custom_1_value": "Absender Zusatzwert 1",
        "sender_custom_2_key": "Absender Zusatzschlüssel 2",
        "sender_custom_2_value": "Absender Zusatzwert 2",
        "sender_custom_3_key": "Absender Zusatzschlüssel 3",
        "sender_custom_3_value": "Absender Zusatzwert 3",
        "sender_phone": "Absender Telefon",
        "sender_mobile_phone": "Absender Mobiltelefon",
        "sender_fax": "Absender Fax",
        "sender_email": "Absender E-Mail",
        "sender_url": "Absender URL",
        "sender_bank": "Absender Bankverbindung",
        "sender_logo": "Absender Logo",
        "sender_backaddress_separator": "Rücksendeadress-Trennzeichen",
        "my_reference": "Mein Zeichen",
        "signature": "Unterschrift",
        "recipient_last_name": "Empfänger Nachname",
        "recipient_first_name": "Empfänger Vorname",
        "recipient_title": "Empfänger Titel",
        "recipient_extra": "Empfänger Zusatz",
        "recipient_street": "Empfänger Straße",
        "recipient_street_number": "Empfänger Nummer",
        "recipient_postal_code": "Empfänger PLZ",
        "recipient_city": "Empfänger Ort",
        "your_reference": "Ihr Zeichen",
        "your_mail": "Ihr Schreiben",
        "customer": "Kundennummer",
        "invoice": "Rechnungsnummer",
        "letter_title": "Brieftitel",
        "subject": "Betreff",
        "subject_separator": "Betreff-Trennzeichen",
        "opening": "Anrede",
        "body": "Brieftext",
        "closing": "Grußformel",
        "ps": "Postskriptum",
        "cc": "Verteiler",
        "cc_separator": "Verteiler-Trennzeichen",
        "encl": "Anlagen",
        "encl_separator": "Anlagen-Trennzeichen",
        "place": "Ort",
        "place_separator": "Ort-Datum-Trennzeichen",
        "filename_addressee": "Dateiname Empfänger",
    }
    return labels[key]
