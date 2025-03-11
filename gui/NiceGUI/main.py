from nicegui import ui
from pathlib import Path
from __init__ import albert_letter  # Import your letter generation function


def generate_letter():
    """Generate a letter PDF using the form input and display a download link."""
    output_path = Path("Documents/Letter")
    output_path.mkdir(parents=True, exist_ok=True)

    albert_letter(
        to_name=name_input.value,
        to_address=address_input.value,
        to_zip=zip_input.value,
        to_city=city_input.value,
        opening=opening_input.value,
        body=body_input.value,
        closing=closing_input.value,
        subject=subject_input.value,
    )

    pdf_path = output_path / f"{name_input.value}.pdf"
    pdf_link.set_text(f"Download PDF: {pdf_path}")
    pdf_link.set_visibility(True)


# UI Components
ui.label("Letter Generator").classes("text-2xl")

with ui.row():
    name_input = ui.input("Recipient Name").classes("w-1/2")
    address_input = ui.input("Street and House Number").classes("w-1/2")

with ui.row():
    zip_input = ui.input("ZIP Code").classes("w-1/3")
    city_input = ui.input("City").classes("w-2/3")

subject_input = ui.input("Subject").classes("w-full")
opening_input = ui.input("Opening (e.g., Dear Sir/Madam)").classes("w-full")
body_input = ui.textarea("Body of the Letter").classes("w-full h-40")
closing_input = ui.input("Closing (e.g., Sincerely)").classes("w-full")

ui.button("Generate PDF", on_click=generate_letter)

pdf_link = ui.label("").classes("text-blue-500").set_visibility(False)

ui.run()
