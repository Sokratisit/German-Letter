from nicegui import ui
import latex  # Import your existing LaTeX handling functions

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
        # "closing": closing.value,
        # "date": date.value,
    }
    if closing.value:
        context["closing"] = closing.value
    if date.value:
        context["date"] = date.value

    try:
        latex.main(**context)  # Call the function that renders LaTeX and generates the PDF
        ui.notify("PDF successfully generated!", type="positive")
    except Exception as e:
        ui.notify(f"Error: {str(e)}", type="negative")

ui.label("Letter Generator").classes("text-2xl font-bold mb-4")

with ui.column().classes("w-full max-w-lg"):
    from_name = ui.input("Sender Name").classes("w-full")
    from_address = ui.input("Sender Address").classes("w-full")
    from_zip_code = ui.input("Sender ZIP Code").classes("w-full")
    from_city = ui.input("Sender City").classes("w-full")
    from_phone = ui.input("Sender Phone").classes("w-full")
    from_email = ui.input("Sender Email").classes("w-full")
    my_ref = ui.input("My Reference").classes("w-full")
    your_ref = ui.input("Your Reference").classes("w-full")  # Correct name

    to_name = ui.input("Recipient Name").classes("w-full")
    to_address = ui.input("Recipient Address").classes("w-full")
    to_zip = ui.input("Recipient ZIP Code").classes("w-full")
    to_city = ui.input("Recipient City").classes("w-full")

    opening = ui.input("Opening (e.g., 'Dear Mr. Smith')").classes("w-full")
    body = ui.textarea("Body").classes("w-full")
    closing = ui.input("Closing (e.g., 'Sincerely')").classes("w-full")
    date = ui.input("Date (Leave blank for today)").classes("w-full")

    ui.button("Generate Letter", on_click=generate_letter).classes("mt-4")
