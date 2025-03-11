from nicegui import ui
import latex  # Import your existing LaTeX handling functions

### 📌 Sender Template Functions ###
def autofill_sender_albert():
    from_name.value = "Albert Marks"
    from_address.value = "Stammheimer Str. 94"
    from_zip_code.value = "50735"
    from_city.value = "Köln"

def autofill_sender_max():
    from_name.value = "Max Mustermann"
    from_address.value = "Musterstraße 123"
    from_zip_code.value = "12345"
    from_city.value = "Musterstadt"

### 📌 Receiver Template Functions ###
def autofill_receiver_schwerbehindertenstelle():
    to_address.value = r"Schwerbehindertenstelle\\Ottmar-Pohl-Platz 1"
    to_zip.value = "51103"
    to_city.value = "Köln"

### 📌 Autofill Phone and Email ###
def autofill_phone_landline():
    from_phone.value = "+49 221 1234567"

def autofill_email_german():
    from_email.value = "albertmarks@gmx.de"

def autofill_email_uni():
    from_email.value = "amarks2@smail.uni-koeln.de"

def autofill_email_google():
    from_email.value = "neosokratis@gmail.com"

### 📌 Generate Letter ###
def generate_letter():
    context = {
        "from_name": from_name.value,
        "from_address": from_address.value,
        "from_zip": from_zip_code.value,
        "from_city": from_city.value,
        "place": from_city.value,
        "from_phone": from_phone.value,
        "from_email": from_email.value,
        "my_ref": my_ref.value,
        "your_ref": your_ref.value,
        "to_name": to_name.value,
        "to_address": to_address.value,
        "to_zip": to_zip.value,
        "to_city": to_city.value,
        "opening": opening.value,
        "body": body.value,
    }
    if closing.value:
        context["closing"] = closing.value
    if date.value:
        context["date"] = date.value

    try:
        latex.main(**context)
        ui.notify("📄 PDF erfolgreich generiert!", type="positive")
    except Exception as e:
        ui.notify(f"❌ Fehler: {str(e)}", type="negative")

# UI Start
ui.label("📜 Brief-Generator").classes("text-2xl font-bold mb-4")

# Sender
ui.label("✉️ Absender").classes("text-lg font-bold mt-2")
with ui.row():
    ui.button("Albert Marks", on_click=autofill_sender_albert).classes("bg-blue-500 text-white shrink-0")
    ui.button("Max Mustermann", on_click=autofill_sender_max).classes("bg-blue-500 text-white shrink-0")

with ui.row().classes("w-full max-w-5xl gap-4"):

    with ui.column():
        from_name = ui.input("Name des Absenders").classes("w-full")
        from_address = ui.input("Adresse des Absenders").classes("w-full")
        from_zip_code = ui.input("PLZ des Absenders").classes("w-full")
        from_city = ui.input("Stadt des Absenders").classes("w-full")

    with ui.column():
        # ui.label("📞 Kontaktinformationen").classes("text-lg font-bold mt-2")
        with ui.row().classes("w-full"):
            my_ref = ui.input("Mein Zeichen (optional)").classes("w-full")
            from_phone = ui.input("Telefonnummer (optional)").classes("flex-grow")
            ui.button("📞 Festnetz", on_click=autofill_phone_landline).classes("bg-gray-300 shrink-0")

        # ui.label("📧 E-Mail").classes("text-lg font-bold mt-2")
        with ui.row().classes("w-full flex-wrap gap-2"):
            from_email = ui.input("E-Mail (optional)").classes("flex-grow")
            ui.button("📧 GMX", on_click=autofill_email_german).classes("bg-gray-300 shrink-0")
            ui.button("📧 Universität", on_click=autofill_email_uni).classes("bg-gray-300 shrink-0")
            ui.button("📧 GMail", on_click=autofill_email_google).classes("bg-gray-300 shrink-0")

# Receiver
ui.label("📬 Empfänger").classes("text-lg font-bold mt-2")
with ui.row():
    ui.button("Schwerbehindertenstelle", on_click=autofill_receiver_schwerbehindertenstelle).classes(
        "bg-purple-500 text-white shrink-0")

with ui.row().classes("w-full max-w-5xl gap-4"):
    with ui.column():
        to_name = ui.input("Name des Empfängers").classes("w-full")
        to_address = ui.input("Adresse des Empfängers").classes("w-full")
        to_zip = ui.input("PLZ des Empfängers").classes("w-full")
        to_city = ui.input("Stadt des Empfängers").classes("w-full")

    with ui.column():
        your_ref = ui.input("Ihr Zeichen (optional)").classes("w-full")

# Main Letter Content
ui.label("📝 Briefinhalt").classes("text-lg font-bold mt-2")
opening = ui.input("Anrede (z. B. 'Sehr geehrte Damen und Herren,')").classes("w-full")
body = ui.textarea("Brieftext").classes("w-full")

ui.label("✍️ Schluss").classes("text-lg font-bold mt-2")
closing = ui.input("Schlussformel (z. B. 'Mit freundlichen Grüßen')").classes("w-full")
date = ui.input("Datum (leer lassen für heutiges Datum)").classes("w-full")

# Generate Letter Button (Full Width)
ui.button("📄 Brief generieren", on_click=generate_letter).classes("mt-4 bg-green-500 text-white w-full")
