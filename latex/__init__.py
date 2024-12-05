import re
import shutil
import subprocess
from datetime import datetime
from pathlib import Path

import send2trash
from jinja2 import Environment, FileSystemLoader


def render_template(template_name: str, output_path: Path, context: dict) -> None:
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

    # Clean up excessive newlines
    cleaned_content = clean_newlines(rendered_content)

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(cleaned_content)


def generate_pdf(tex_path: Path, output_dir: Path) -> None:
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


def format_address_for_latex(address: str, name: str | None = None) -> str:
    """
    Format an address string for LaTeX.

    :param name: The name of the recipient.
    :param address: The input address string, which may include '\n', ', ', or ','.
    :return: A properly formatted LaTeX string where '\n', ', ', and ',' are replaced with ' \\ '.
    """
    if not address and not name:
        return ''

    # Replace address separators with LaTeX line breaks
    modified_address = ''
    if name:
        madified_address = name + r' \\ '
    modified_address += address.replace('\n', r' \\ ').replace(', ', r' \\ ').replace(',', r' \\ ')
    return modified_address


def generate_backaddress(
        from_name: str,
        from_address: str | None = None,
        from_zip: str | None = None,
        from_city: str | None = None,
        separator: str = ', ') -> str :
    """
    Generate the backaddress by abbreviating the first name and combining it with the address.

    :param from_name: Full name of the sender.
    :param from_address: Full address of the sender. If None, no backaddress is generated.
    :param from_zip: ZIP code of the sender.
    :param from_city: City of the sender.
    :param separator: Separator to use between the name and the address components.
    :return: The formatted backaddress, or None if required inputs are missing.
    """
    if not from_name or not from_address:
        return ''

    # Normalize the address to a single line, removing any '\n' or redundant separators
    normalized_address = from_address.replace('\n', separator).replace(', ', separator).replace(',', separator).strip()

    # Split the name into first and last parts
    name_parts = from_name.split()
    if len(name_parts) < 2:
        name_str = from_name
    else:
        # Modify the name to include only the first initial
        first_initial = name_parts[0][0] + '.'
        last_name = ' '.join(name_parts[1:])  # Handle compound last names
        name_str = f'{first_initial} {last_name}'

    # ZIP code and city
    if from_zip and from_city:
        city_str = f'{from_zip} {from_city}'
    elif from_zip:
        city_str = from_zip
    elif from_city:
        city_str = from_city
    else:
        city_str = ''

    all_parts = (name_str, normalized_address, city_str)
    cleaned_parts = [part for part in all_parts if part]  # Remove empty parts

    return separator.join(cleaned_parts)


def generate_filename(recipient_name: str) -> str:
    """
    Generate a unique filename based on the current timestamp.

    :param recipient_name: The name of the letter's addressee.
    :return: A unique filename in the format 'YYYYMMDD_HHMMSS'.
    """
    now = datetime.now()
    return f'{now.strftime('%Y-%m-%d')} {recipient_name}'


def setup_output_directories(base_path: Path) -> tuple[Path, Path]:
    """
    Setup output directories for the PDF and LaTeX files.

    :param base_path: The base directory for letters.
    :return: A tuple containing paths to the PDF directory and LaTeX directory.
    """
    pdf_dir = base_path / 'Letter'
    latex_dir = pdf_dir / 'LaTeX'

    pdf_dir.mkdir(parents=True, exist_ok=True)
    latex_dir.mkdir(parents=True, exist_ok=True)

    return pdf_dir, latex_dir


def move_files(src_dir: Path, dest_dir: Path, patterns: list[str]) -> None:
    """
    Move specific files from the source directory to the destination directory.

    :param src_dir: Source directory containing the files.
    :param dest_dir: Destination directory where files should be moved.
    :param patterns: List of file patterns (e.g., ['*.pdf', '*.tex']).
    :return: None
    """
    for pattern in patterns:
        for file in src_dir.glob(pattern):
            dest_path = dest_dir / file.name
            shutil.move(str(file), str(dest_path))
            print(f"Moved: {file} -> {dest_path}")


def trash_files(src_dir: Path, extensions: list[str] | None = None) -> None:
    """
    Move unwanted files to the system trash.

    :param src_dir: Directory containing the files to trash.
    :param extensions: List of file extensions to move to the trash. Defaults to ['.aux', '.log', '.out', '.toc'].
    :return: None
    """
    if extensions is None:
        extensions = ['.aux', '.log', '.out', '.toc']  # Default extensions

    for file in src_dir.iterdir():
        if file.suffix in extensions:
            send2trash.send2trash(str(file))
            print(f"Trashed: {file}")


def clean_latex_files(latex_dir: Path, extensions: list[str] | None = None) -> None:
    """
    Delete temporary LaTeX files from the LaTeX directory.

    :param latex_dir: Path to the directory containing LaTeX files.
    :param extensions: List of file extensions to remove. Defaults to ['.aux', '.log', '.out', '.toc'].
    :return: None
    """
    if extensions is None:
        extensions = ['.aux', '.log', '.out', '.toc']  # Default extensions

    for file in latex_dir.iterdir():
        if file.suffix in extensions:
            file.unlink()
            print(f"Deleted: {file}")


def clean_newlines(content: str) -> str:
    """
    Replace multiple consecutive newlines in the content with exactly two newlines.

    :param content: The LaTeX content as a string.
    :return: The cleaned content with no more than two consecutive newlines.
    """
    return re.sub(r'\n{3,}', '\n\n', content)


def main(
        to_name: str,
        to_address: str,
        to_zip: str,
        to_city: str,
        opening: str,
        body: str,
        from_name: str,
        closing: str = 'Mit freundlichen Grüßen',
        from_address: str | None = None,
        from_zip: str | None = None,
        from_city: str | None = None,
        back_address_separator: str = ', ',
        from_phone: str | None = None,
        from_mobile_phone: str | None = None,
        from_email: str | None = None,
        my_ref: str | None = None,
        subject: str | None = None,
        back_address: str | None = None,
        place: str | None = None,
        date: str | None = None,
        filename: str | None = None,
        additional_info: dict[str, str] | None = None,
) -> None:
    """
    Main function to create a letter and generate a PDF.

    :param from_name: Full name of the sender.
    :param to_name: Full name of the recipient.
    :param to_address: Full address of the recipient, including name.
    :param to_zip: ZIP code of the recipient.
    :param to_city: City of the recipient.
    :param opening: Letter's opening (e.g., 'Dear').
    :param body: Main content of the letter.
    :param closing: Closing remarks (e.g., 'Sincerely').
    :param from_address: Optional sender's address.
    :param from_zip: Optional sender's ZIP code.
    :param from_city: Optional sender's city.
    :param back_address_separator: Separator to use between the name and the address components.
    :param from_phone: Optional sender's phone number.
    :param from_mobile_phone: Optional sender's mobile phone number.
    :param from_email: Optional sender's email address.
    :param my_ref: Optional reference number of the sender.
    :param subject: Optional subject of the letter.
    :param back_address: Optional back-address; auto-generated if not provided.
    :param place: Optional place to include in the date.
    :param date: Optional date in the format 'DD.MM.YYYY'. Generated automatically if `None`.
    :param filename: Optional filename for the generated PDF.
    :param additional_info: Optional additional information to include in the sender's address.
    :return: None
    """
    # Directories
    output_dir = Path('output')  # Temporary directory for the generated files
    user_path = Path.home()
    documents_path = user_path / 'Documents'
    letters_dir = documents_path / 'Letter' # Directory for the final PDFs
    latex_dir = letters_dir / 'LaTeX'  # Directory for the LaTeX files

    output_dir.mkdir(parents=True, exist_ok=True)
    letters_dir.mkdir(parents=True, exist_ok=True)
    latex_dir.mkdir(parents=True, exist_ok=True)

    # Generate back-address if not provided
    if not back_address:
        back_address = generate_backaddress(from_name, from_address, from_zip, from_city, separator=back_address_separator)

    # Add additional data to the end of the address
    if additional_info:
        from_address += '\n' + ', '.join(f'{key}:\\quad{value}' for key, value in additional_info.items())

    # Format addresses for LaTeX
    to_address += ', '.join([to_zip, to_city])
    formatted_from_address = format_address_for_latex(address=from_address) if from_address else None
    formatted_recipient_address = format_address_for_latex(address=to_address, name=to_name)

    # Generate the date if not provided
    if not date:
        now = datetime.now()
        date = now.strftime('%d.%m.%Y')  # Format date as DD.MM.YYYY
    formatted_date = f'{place}, {date}' if place else date

    # Generate a filename if not provided
    if not filename:
        filename = generate_filename(to_name)

    # Define the output paths
    output_tex_path = output_dir / f'{filename}.tex'

    # Context for the LaTeX template
    context = {
        'from_name': from_name,
        'from_address': formatted_from_address,
        'from_zip_code': from_zip,
        'from_city': from_city,
        'from_phone': from_phone,
        'from_mobile_phone': from_mobile_phone,
        'from_email': from_email,
        'my_ref': my_ref,
        'subject': subject,
        'to_name': to_name,
        'to_address': formatted_recipient_address,
        'opening': opening,
        'body': body,
        'closing': closing,
        'back_address': back_address,
        'date': formatted_date,  # Inject the formatted date
        'additional_info': additional_info  # data to be added to the sender's address
    }

    # Render the template
    render_template('letter_template.jinja', output_tex_path, context)

    # Generate the PDF
    try:
        generate_pdf(output_tex_path, output_dir)

        # Move PDF and LaTeX files to their respective directories
        move_files(output_dir, letters_dir, ['*.pdf'])
        move_files(output_dir, latex_dir, ['*.tex'])

        # Trash auxiliary LaTeX files
        trash_files(output_dir)

        # Open the generated PDF
        pdf_path = letters_dir / f'{filename}.pdf'
        subprocess.run(['start', '', str(pdf_path)], shell=True)

    except Exception as e:
        print(f"Error occurred: {e}")
        print(f"Files left in: {output_dir} for debugging.")
