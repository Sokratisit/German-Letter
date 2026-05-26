import json

from app import create_app


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
        "sender_custom_1_key": "Yahoo",
        "sender_custom_1_value": "some_username",
        "sender_custom_2_key": "",
        "sender_custom_2_value": "",
        "sender_custom_3_key": "",
        "sender_custom_3_value": "",
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


def test_index_prefills_sender_and_recipient_from_cookies() -> None:
    app = create_app()
    client = app.test_client()
    client.set_cookie("letter_sender", json.dumps({"sender_last_name": "Muster", "sender_city": "Köln"}))
    client.set_cookie("letter_recipient", json.dumps({"recipient_last_name": "Beispiel", "customer": "4711"}))

    response = client.get("/")

    body = response.get_data(as_text=True)
    assert response.status_code == 200
    assert 'value="Muster"' in body
    assert 'value="Köln"' in body
    assert 'value="Beispiel"' in body
    assert 'value="4711"' in body
    assert 'id="save_sender" name="save_sender" type="checkbox" checked' in body
    assert 'id="save_recipient" name="save_recipient" type="checkbox" checked' in body
    assert 'id="body_mode_markdown" name="body_mode" type="radio" value="markdown" checked' in body
    assert 'href="/anleitung"' in body


def test_guide_page_links_back_to_main_page() -> None:
    app = create_app()
    client = app.test_client()

    response = client.get("/anleitung")

    body = response.get_data(as_text=True)
    assert response.status_code == 200
    assert "<h1>Anleitung</h1>" in body
    assert 'href="/"' in body


def test_generate_sets_sender_and_recipient_cookies(monkeypatch) -> None:
    app = create_app()
    client = app.test_client()

    monkeypatch.setattr("app.routes.render_letter_pdf", lambda *_args, **_kwargs: ("2026-04-24 Beispiel.pdf", b"%PDF-1.4"))
    payload = _valid_payload() | {"save_sender": "on", "save_recipient": "on"}

    response = client.post("/generate", data=payload)

    set_cookies = response.headers.getlist("Set-Cookie")
    assert response.status_code == 200
    assert response.mimetype == "application/pdf"
    assert any(cookie.startswith("letter_sender=") for cookie in set_cookies)
    assert any(cookie.startswith("letter_recipient=") for cookie in set_cookies)


def test_generate_deletes_unchecked_cookies(monkeypatch) -> None:
    app = create_app()
    client = app.test_client()
    client.set_cookie("letter_sender", json.dumps({"sender_last_name": "Alt"}))
    client.set_cookie("letter_recipient", json.dumps({"recipient_last_name": "Alt"}))

    monkeypatch.setattr("app.routes.render_letter_pdf", lambda *_args, **_kwargs: ("2026-04-24 Beispiel.pdf", b"%PDF-1.4"))
    response = client.post("/generate", data=_valid_payload())

    set_cookies = response.headers.getlist("Set-Cookie")
    assert any(cookie.startswith("letter_sender=;") for cookie in set_cookies)
    assert any(cookie.startswith("letter_recipient=;") for cookie in set_cookies)


def test_index_prefers_query_parameters_over_cookies_per_field() -> None:
    app = create_app()
    client = app.test_client()
    client.set_cookie("letter_sender", json.dumps({"sender_last_name": "CookieName", "sender_city": "Köln"}))
    client.set_cookie("letter_recipient", json.dumps({"recipient_last_name": "CookieRecipient", "recipient_city": "Hamburg"}))

    response = client.get(
        "/?from_name_last=QueryName&to_name_last=QueryRecipient&place=Berlin&fromcustom1key=Yahoo"
    )

    body = response.get_data(as_text=True)
    assert response.status_code == 200
    assert 'name="sender_last_name" type="text"' in body
    assert 'value="QueryName"' in body
    assert 'name="sender_city" type="text"' in body
    assert 'value="Köln"' in body
    assert 'name="recipient_last_name" type="text"' in body
    assert 'value="QueryRecipient"' in body
    assert 'name="recipient_city" type="text"' in body
    assert 'value="Hamburg"' in body
    assert 'name="place" type="text" value="Berlin"' in body
    assert 'name="sender_custom_1_key" type="text" value="Yahoo"' in body


def test_faq_and_terms_do_not_link_to_guide() -> None:
    app = create_app()
    client = app.test_client()

    faq_response = client.get("/faq")
    terms_response = client.get("/bedingungen")

    faq_body = faq_response.get_data(as_text=True)
    terms_body = terms_response.get_data(as_text=True)

    assert faq_response.status_code == 200
    assert terms_response.status_code == 200
    assert 'href="/anleitung"' not in faq_body
    assert 'href="/anleitung"' not in terms_body
