from datetime import datetime

import FreeSimpleGUI as sg

from database import load_configs
import latex

# Load sender and receiver data
senders, receivers = load_configs()

# Prepare combo options with an empty entry
sender_options = [""] + list(senders.keys())
receiver_options = [""] + list(receivers.keys())

# Initialize tracking variables
current_sender_choice = None
current_receiver_choice = None

# GUI layout
title = 'Brief erstellen'
WIDTH_LEFT = 15

layout = [
    [
        sg.Text('Sender', size=(WIDTH_LEFT, 1)),
        sg.Combo(sender_options, key='sender_choice', readonly=True, enable_events=True),
        sg.Text('Empfänger'),
        sg.Combo(receiver_options, key='receiver_choice', readonly=True, enable_events=True),
    ],
    [
        sg.Text('Sendername', size=(WIDTH_LEFT, 1)),
        sg.InputText(key='from_name', enable_events=True),
    ],
    [
        sg.Text('Senderstraße', size=(WIDTH_LEFT, 1)),
        sg.InputText(key='from_address', enable_events=True),
    ],
    [
        sg.Text('Sender-PLZ', size=(WIDTH_LEFT, 1)),
        sg.InputText(key='from_zip', enable_events=True),
    ],
    [
        sg.Text('Sender-Ort', size=(WIDTH_LEFT, 1)),
        sg.InputText(key='from_city', enable_events=True),
    ],
    [
        sg.Text('Zusatz', size=(WIDTH_LEFT, 1)),
        sg.InputText(key='additional_info'),
    ],
    [
        sg.Text('Rückaddresse', size=(WIDTH_LEFT, 1)),
        sg.InputText(key='back_address'),
    ],
    [
        sg.Text('Festnetznummer', size=(WIDTH_LEFT, 1)),
        sg.InputText(key='from_phone'),
    ],
    [
        sg.Text('Mobilnummer', size=(WIDTH_LEFT, 1)),
        sg.InputText(key='from_mobile_phone'),
    ],
    [
        sg.Text('E-Mail', size=(WIDTH_LEFT, 1)),
        sg.InputText(key='from_email'),
    ],
    [
        sg.Text('Meine Referenz', size=(WIDTH_LEFT, 1)),
        sg.InputText(key='my_ref'),
    ],
    [
        sg.Text('Zusatzinfo', size=(WIDTH_LEFT, 1)),
        sg.InputText(key='place'),
    ],
    [
        sg.Text('Datum', size=(WIDTH_LEFT, 1)),
        sg.InputText(key='date'),
    ],
    [
        sg.Text('Empfängername', size=(WIDTH_LEFT, 1)),
        sg.InputText(key='to_name', enable_events=True),
    ],
    [
        sg.Text('Empfängerstraße', size=(WIDTH_LEFT, 1)),
        sg.InputText(key='to_address'),
    ],
    [
        sg.Text('Empfänger-PLZ', size=(WIDTH_LEFT, 1)),
        sg.InputText(key='to_zip'),
    ],
    [
        sg.Text('Empfänger-Ort', size=(WIDTH_LEFT, 1)),
        sg.InputText(key='to_city'),
    ],
    [
        sg.Text('Betreff', size=(WIDTH_LEFT, 1)),
        sg.InputText(key='subject'),
    ],
    [
        sg.Text('Anrede', size=(WIDTH_LEFT, 1)),
        sg.InputText(key='opening'),
    ],
    [
        sg.Text('Text', size=(WIDTH_LEFT, 1)),
        sg.Multiline(key='text', size=(50, 10)),
    ],
    [
        sg.Text('Grußformel', size=(WIDTH_LEFT, 1)),
        sg.InputText(key='closing', default_text='Mit freundlichen Grüßen'),
    ],
    [
        sg.Text('Name', size=(WIDTH_LEFT, 1)),
        sg.InputText(key='signature'),
    ],
    [
        sg.Text('Dateiname', size=(WIDTH_LEFT, 1)),
        sg.InputText(key='filename'),
    ],
    [sg.Button('Generate'), sg.Button('Cancel')]
]

window = sg.Window(title, layout)


def main() -> None:
    global current_sender_choice, current_receiver_choice

    while True:
        event, values = window.read()

        if event in (sg.WIN_CLOSED, 'Cancel'):
            break

        # Handle sender selection
        if event == 'sender_choice':
            selected_sender = values['sender_choice']
            if selected_sender == '':
                # Clear sender fields if empty
                keys = senders[current_sender_choice].keys()
                for key in keys:
                    window[key].update('')
                if 'from_name' in keys:
                    window['signature'].update('')

                # Clear back-address field
                window['back_address'].update('')

                current_sender_choice = None
            elif selected_sender != current_sender_choice:
                # Update sender fields
                keys = senders[selected_sender].keys()
                for key in keys:
                    window[key].update(senders[selected_sender][key])
                if 'from_name' in keys:
                    window['signature'].update(senders[selected_sender]['from_name'])
                if 'from_phone' not in keys:
                    window['from_phone'].update('')
                if 'from_mobile_phone' not in keys:
                    window['from_mobile_phone'].update('')
                if 'from_email' not in keys:
                    window['from_email'].update('')

                # Generate back-address
                back_address = latex.generate_backaddress(from_name=window['from_name'].get(), from_address=window[
                    'from_address'].get(), from_zip=window['from_zip'].get(), from_city=window['from_city'].get())
                window['back_address'].update(back_address)

                current_sender_choice = selected_sender

        # Handle receiver selection
        elif event == 'receiver_choice':
            selected_receiver = values['receiver_choice']
            if selected_receiver == '':
                # Clear receiver fields if empty
                keys = receivers[current_receiver_choice].keys()
                for key in keys:
                    window[key].update('')

                # Clear the filename field
                window['filename'].update('')

                current_receiver_choice = None
            elif selected_receiver != current_receiver_choice:
                # Update receiver fields
                keys = receivers[selected_receiver].keys()
                for key in keys:
                    window[key].update(receivers[selected_receiver][key])

                # Generate filename
                date_str = datetime.now().strftime('%Y-%m-%d')
                name = window['to_name'].get()
                filename = f'{date_str} {name}'
                window['filename'].update(filename)

                current_receiver_choice = selected_receiver

        elif event == 'from_name':
            # Update signature when from_name changes
            name = window['from_name'].get()
            window['signature'].update(name)

            # Update back-address when from_name changes
            back_address = latex.generate_backaddress(from_name=name, from_address=values['from_address'], from_zip=values['from_zip'], from_city=values['from_city'])
            if back_address is None:
                back_address = ''
            window['back_address'].update(back_address)

        elif event in ('from_address', 'from_zip', 'from_city'):
            # Update back-address when from_address changes
            back_address = latex.generate_backaddress(from_name=values['from_name'], from_address=values['from_address'], from_zip=values['from_zip'], from_city=values['from_city'])
            if back_address is None:
                back_address = ''
            window['back_address'].update(back_address)

        # When the name of the receiver changes, update the filename
        elif event == 'to_name':
            # Update filename when to_name changes
            date_str = datetime.now().strftime('%Y-%m-%d')
            name = window['to_name'].get()
            filename = f'{date_str} {name}'
            window['filename'].update(filename)

        elif event == 'Generate':
            latex.main(
                to_name=values['to_name'],
                to_address=values['to_address'],
                to_zip=values['to_zip'],
                to_city=values['to_city'],
                opening=values['opening'],
                body=values['text'],
                from_name=values['from_name'],
                closing=values['closing'],
                from_address=values['from_address'],
                from_zip=values['from_zip'],
                from_city=values['from_city'],
                from_phone=values['from_phone'],
                from_mobile_phone=values['from_mobile_phone'],
                from_email=values['from_email'],
                my_ref=values['my_ref'],
                subject=values['subject'],
                back_address=values['back_address'],
                place=values['place'],
                date=values['date'],
                # signature=values['signature'],  # TODO: Implement signature
                filename=values['filename'],
                # additional_info=values['additional_info']  # TODO: convert given string to dictionary
            )

    window.close()
