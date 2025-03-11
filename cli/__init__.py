import questionary
import sys

import latex


def main() -> None:
    try:
        recipient_name = input('Name des Empfängers: ')
        recipient_street = input('Straße des Empfängers: ')
        recipient_zip = input('PLZ des Empfängers: ')
        recipient_city = input('Ort des Empfängers: ')
        opening = input('Anrede: ')
        body = input('Text: ')
        print('Erstelle Brief...')
        latex.albert_letter(
            to_name=recipient_name,
            to_address=recipient_street,
            to_zip=recipient_zip,
            to_city=recipient_city,
            opening=opening,
            body=body,
        )
    except KeyboardInterrupt:
        print('Abbruch')
        sys.exit(0)
