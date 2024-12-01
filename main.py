import os
import subprocess
from datetime import datetime

from jinja2 import Environment, FileSystemLoader


def render_template(template_name: str, output_path: str, context: dict) -> None:
    """
    Render a Jinja2 template with the given context and save it to a file.

    :param template_name: The name of the Jinja2 template file.
    :param output_path: The path where the rendered file will be saved.
    :param context: A dictionary containing context variables to render the template.
    :return: None
    """
    env = Environment(loader=FileSystemLoader('templates'))
    template = env.get_template(template_name)
    rendered_content = template.render(context)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(rendered_content)


def generate_pdf(tex_path: str, output_dir: str) -> None:
    """
    Generate a PDF from a LaTeX file using pdflatex.

    :param tex_path: The path to the .tex file to compile.
    :param output_dir: The directory where the generated PDF will be saved.
    :return: None
    :raises RuntimeError: If the pdflatex command fails.
    """
    try:
        subprocess.run(
            ['pdflatex', '-output-directory', output_dir, tex_path],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
    except subprocess.CalledProcessError as e:
        error_message = e.stderr.decode()
        print(f"Error while generating PDF:\n{error_message}")
        raise RuntimeError(f"pdflatex failed with error:\n{error_message}")


def format_address_for_latex(address: str) -> str:
    """
    Format an address string for LaTeX.

    :param address: The input address string, which may include '\n', ', ', or ','.
    :return: A properly formatted LaTeX string where '\n', ', ', and ',' are replaced with ' \\ '.
    """
    if not address:
        return ''

    # Replace address separators with LaTeX line breaks
    return address.replace('\n', r' \\ ').replace(', ', r' \\ ').replace(',', r' \\ ')


def generate_backaddress(from_name: str, from_address: str | None, separator: str = ', ') -> str | None:
    """
    Generate the backaddress by abbreviating the first name and combining it with the address.

    :param from_name: Full name of the sender.
    :param from_address: Full address of the sender. If None, no backaddress is generated.
    :param separator: Separator to use between the name and the address components.
    :return: The formatted backaddress, or None if required inputs are missing.
    """
    if not from_name or not from_address:
        return None

    # Normalize the address to a single line, removing any '\n' or redundant separators
    normalized_address = from_address.replace('\n', separator).replace(', ', separator).replace(',', separator).strip()

    # Split the name into first and last parts
    name_parts = from_name.split()
    if len(name_parts) < 2:
        return f'{from_name}{separator}{normalized_address}'  # Use full name if no last name

    # Create the backaddress
    first_initial = name_parts[0][0] + '.'
    last_name = ' '.join(name_parts[1:])  # Handle compound last names
    return f'{first_initial} {last_name}{separator}{normalized_address}'


def main(
    from_name: str,
    recipient_address: str,
    opening: str,
    body: str,
    closing: str,
    from_address: str | None = None,
    from_phone: str | None = None,
    from_email: str | None = None,
    subject: str | None = None,
    backaddress: str | None = None,
    place: str | None = None,
    date: str | None = None,
) -> None:
    """
    Main function to create a letter and generate a PDF.

    :param from_name: Full name of the sender.
    :param recipient_address: Full address of the recipient, including name.
    :param opening: Letter's opening (e.g., 'Dear').
    :param body: Main content of the letter.
    :param closing: Closing remarks (e.g., 'Sincerely').
    :param from_address: Optional sender's address.
    :param from_phone: Optional sender's phone number.
    :param from_email: Optional sender's email address.
    :param subject: Optional subject of the letter.
    :param backaddress: Optional backaddress; auto-generated if not provided.
    :param place: Optional place to include in the date.
    :param date: Optional date in the format 'DD.MM.YYYY'. Generated automatically if None.
    :return: None
    """
    # Generate backaddress if not provided
    if not backaddress:
        backaddress = generate_backaddress(from_name, from_address)

    # Format addresses for LaTeX
    # formatted_from_address = format_address_for_latex(from_address) if from_address else None
    formatted_from_address = from_address
    formatted_recipient_address = format_address_for_latex(recipient_address)

    # Generate the date if not provided
    if not date:
        now = datetime.now()
        date = now.strftime('%d.%m.%Y')  # Format date as DD.MM.YYYY
    formatted_date = f'{place}, {date}' if place else date

    # Define the output paths
    output_dir = 'output'
    os.makedirs(output_dir, exist_ok=True)
    tex_path = os.path.join(output_dir, 'letter.tex')
    pdf_path = os.path.join(output_dir, 'letter.pdf')

    # Context for the LaTeX template
    context = {
        'from_name': from_name,
        'from_address': formatted_from_address,
        'from_phone': from_phone,
        'from_email': from_email,
        'subject': subject,
        'recipient_address': formatted_recipient_address,
        'opening': opening,
        'body': body,
        'closing': closing,
        'backaddress': backaddress,
        'date': formatted_date,  # Inject the formatted date
    }

    # Render the template
    render_template('letter_template.jinja', tex_path, context)

    # Generate the PDF
    generate_pdf(tex_path, output_dir)
    print(f"PDF generated: {pdf_path}")


if __name__ == '__main__':
    main(
        from_name='John Doe',
        from_address='123 Main Street, City, Country',
        recipient_address='Jane Smith, 456 Another Street, City, Country',
        opening='Dear Jane,',
        body='This is an example letter with an updated date format and place.',
        closing='Sincerely, John Doe',
        from_phone='+123456789',
        from_email='john.doe@example.com',
        subject='Regarding Our Discussion',
        place='Berlin',
        date=None,  # Auto-generate the current date
    )
