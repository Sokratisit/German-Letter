from dataclasses import replace
from datetime import date

from app.latex import (
    build_letter_tex,
    build_output_filename,
    format_german_date,
    write_tex_file,
)
from app.validation import LetterFormData


def _letter_data() -> LetterFormData:
    return LetterFormData(
        sender_last_name="Mustermann",
        sender_first_name="Max",
        sender_title="Dr.",
        sender_extra="2. Etage",
        sender_street="Musterweg",
        sender_street_number="1",
        sender_postal_code="12345",
        sender_city="Berlin",
        sender_phone="030 123456",
        sender_mobile_phone="0171 2345678",
        sender_fax="030 654321",
        sender_email="max@example.com",
        sender_url="https://example.com",
        sender_bank="IBAN DE21 87654321 13456789\nBIC TESTDEFFXXX",
        sender_logo="",
        sender_backaddress_separator=", ",
        my_reference="MM-42",
        signature="Dr. Max Mustermann",
        recipient_last_name="Beispiel",
        recipient_first_name="Erika",
        recipient_title="Prof.",
        recipient_extra="Personalabteilung",
        recipient_street="Hauptstraße",
        recipient_street_number="5",
        recipient_postal_code="98765",
        recipient_city="Hamburg",
        your_reference="HB-7",
        your_mail="02.04.2026",
        customer="4711",
        invoice="R-77",
        letter_title="Mahnung",
        subject="Test & Anfrage",
        subject_separator=": ",
        opening="Sehr geehrte Frau Beispiel,",
        body="Zeile 1\nZeile 2",
        closing="Mit freundlichen Grüßen",
        ps="Bitte melden Sie sich kurzfristig.",
        cc="Ablage\nVertrieb",
        cc_separator=": ",
        encl="Vertrag\nRechnung",
        encl_separator=": ",
        place="Berlin",
        place_separator=", ",
        date_iso=date(2026, 4, 24),
        filename_addressee="Beispiel",
    )


def test_template_contains_expected_scrlttr2_sections() -> None:
    tex = build_letter_tex(_letter_data())
    assert r"\documentclass[paper=a4,fontsize=11pt]{scrlttr2}" in tex
    assert (
        r"\KOMAoptions{parskip=half,subject=beforeopening,subject=titled,fromphone=true,frommobilephone=true,fromfax=true,fromemail=true,fromurl=true,fromlogo=false}"
        in tex
    )
    assert r"\setlength{\parindent}{0pt}" in tex
    assert r"\setkomavar{fromname}{Dr. Max Mustermann}" in tex
    assert r"\setkomavar{fromaddress}{2. Etage\\ Musterweg 1\\ 12345 Berlin}" in tex
    assert r"\setkomavar{backaddressseparator}{, }" in tex
    assert r"\setkomavar{backaddress}{Dr. M. Mustermann, 2. Etage, Musterweg 1, 12345 Berlin}" in tex
    assert r"\setkomavar*{fromphone}{Telefon: }" in tex
    assert r"\setkomavar*{frommobilephone}{Mobiltelefon: }" in tex
    assert r"\setkomavar*{fromfax}{Fax: }" in tex
    assert r"\setkomavar*{fromemail}{E-Mail: }" in tex
    assert r"\setkomavar*{fromurl}{URL: }" in tex
    assert r"\setkomavar{fromphone}{030 123456}" in tex
    assert r"\setkomavar{frommobilephone}{0171 2345678}" in tex
    assert r"\setkomavar{fromfax}{030 654321}" in tex
    assert r"\setkomavar{fromemail}{max@example.com}" in tex
    assert r"\setkomavar{fromurl}{https://example.com}" in tex
    assert r"\setkomavar{frombank}{IBAN DE21 87654321 13456789\\ BIC TESTDEFFXXX}" in tex
    assert r"\setkomavar*{subject}{Betreff: }" in tex
    assert r"\setkomavar{subject}{Test \& Anfrage}" in tex
    assert r"\setkomavar{title}{Mahnung}" in tex
    assert r"\setkomavar{subjectseparator}{: }" in tex
    assert r"\setkomavar*{yourref}{Ihr Zeichen}" in tex
    assert r"\setkomavar{yourref}{HB-7}" in tex
    assert r"\setkomavar*{yourmail}{Ihr Schreiben vom}" in tex
    assert r"\setkomavar{yourmail}{02.04.2026}" in tex
    assert r"\setkomavar*{myref}{Mein Zeichen}" in tex
    assert r"\setkomavar{myref}{MM-42}" in tex
    assert r"\setkomavar*{customer}{Kundennummer}" in tex
    assert r"\setkomavar{customer}{4711}" in tex
    assert r"\setkomavar*{invoice}{Rechnungsnummer}" in tex
    assert r"\setkomavar{invoice}{R-77}" in tex
    assert r"\setkomavar{place}{}" in tex
    assert r"\setkomavar{placeseparator}{, }" in tex
    assert r"\setkomavar{date}{Berlin, 24.4.2026}" in tex
    assert r"\setkomavar*{date}{Datum}" in tex
    assert r"\setkomavar{toname}{Prof. Erika Beispiel}" in tex
    assert (
        r"\setkomavar{toaddress}{Prof. Erika Beispiel\\ Personalabteilung\\ Hauptstraße 5\\ 98765 Hamburg}"
        in tex
    )
    assert r"\opening{Sehr geehrte Frau Beispiel,}" in tex
    assert r"\ps Bitte melden Sie sich kurzfristig." in tex
    assert r"\par AnlagenVertrag\\ Rechnung" not in tex
    assert r"\par VerteilerAblage\\ Vertrieb" not in tex
    assert r"\par Anlagen: Vertrag\\ Rechnung" in tex
    assert r"\par Verteiler: Ablage\\ Vertrieb" in tex


def test_format_german_date() -> None:
    assert format_german_date(date(2026, 4, 24)) == "24.4.2026"
    assert format_german_date(date(2026, 9, 7)) == "7.9.2026"


def test_write_tex_file(tmp_path) -> None:
    target = tmp_path / "letter.tex"
    write_tex_file(build_letter_tex(_letter_data()), target)
    content = target.read_text(encoding="utf-8")
    assert target.exists()
    assert r"\closing{Mit freundlichen Grüßen}" in content


def test_build_output_filename_uses_date_and_addressee() -> None:
    assert build_output_filename(_letter_data()) == "2026-04-24 Beispiel.pdf"


def test_template_omits_extra_spaces_when_optional_name_parts_are_missing() -> None:
    data = replace(
        _letter_data(),
        sender_first_name="",
        sender_title="",
        recipient_first_name="",
        recipient_title="",
        recipient_extra="",
    )

    tex = build_letter_tex(data)
    assert r"\setkomavar{fromname}{Mustermann}" in tex
    assert r"\setkomavar{backaddress}{Mustermann, 2. Etage, Musterweg 1, 12345 Berlin}" in tex
    assert r"\begin{letter}{Beispiel\\ Hauptstraße 5\\ 98765 Hamburg}" in tex


def test_backaddress_abbreviates_multiple_given_names() -> None:
    data = replace(
        _letter_data(),
        sender_title="Prof. Dr.",
        sender_first_name="Hans Johann",
        sender_last_name="Meyer",
    )
    tex = build_letter_tex(data)
    assert r"\setkomavar{backaddress}{Prof. Dr. H. J. Meyer, 2. Etage, Musterweg 1, 12345 Berlin}" in tex


def test_body_uses_blank_lines_as_paragraph_breaks() -> None:
    data = replace(
        _letter_data(),
        body="Erste Zeile\nZweite Zeile\n\nDritter Absatz",
    )
    tex = build_letter_tex(data)
    assert "Erste Zeile\\\\ Zweite Zeile\n\nDritter Absatz" in tex
