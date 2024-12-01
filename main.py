import os
from jinja2 import Environment, FileSystemLoader
import subprocess

def render_template(template_name, output_path, context):
    """
    Render a Jinja2 template with the given context and save to a file.
    """
    env = Environment(loader=FileSystemLoader('templates'))
    template = env.get_template(template_name)
    rendered_content = template.render(context)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(rendered_content)

def generate_pdf(tex_path, output_dir):
    """
    Generate a PDF from a LaTeX file using pdflatex.
    """
    try:
        subprocess.run(
            ['pdflatex', '-output-directory', output_dir, tex_path],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
    except subprocess.CalledProcessError as e:
        print("Error while generating PDF:", e.stderr.decode())
        raise

def generate_backaddress(from_name, from_address):
    """
    Generate the backaddress by abbreviating the first name and combining it with the address.
    """
    if not from_name or not from_address:
        return None  # Cannot generate backaddress without both name and address

    # Split the name into first and last parts
    name_parts = from_name.split()
    if len(name_parts) < 2:
        return from_name  # If no last name, return the original name

    # Create the backaddress
    first_initial = name_parts[0][0] + "."
    last_name = " ".join(name_parts[1:])  # Handle compound last names
    return f"{first_initial} {last_name}, {from_address}"


def main(from_name, recipient_name, recipient_address, opening, body, closing,
         from_address=None, from_phone=None, from_email=None, subject=None, backaddress=None):
    """
    Main function to create a letter and generate a PDF.
    Mandatory arguments: from_name, recipient_name, recipient_address, opening, body, closing.
    Optional arguments: from_address, from_phone, from_email, subject, backaddress.
    """
    # Generate backaddress if not provided
    if not backaddress:
        backaddress = generate_backaddress(from_name, from_address)

    # Define the output paths
    output_dir = 'output'
    os.makedirs(output_dir, exist_ok=True)
    tex_path = os.path.join(output_dir, 'letter.tex')
    pdf_path = os.path.join(output_dir, 'letter.pdf')

    # Context for the LaTeX template
    context = {
        'from_name': from_name,
        'from_address': from_address,
        'from_phone': from_phone,
        'from_email': from_email,
        'subject': subject,
        'recipient_name': recipient_name,
        'recipient_address': recipient_address,
        'opening': opening,
        'body': body,
        'closing': closing,
        'backaddress': backaddress
    }

    # Render the template
    render_template('letter_template.jinja', tex_path, context)

    # Generate the PDF
    generate_pdf(tex_path, output_dir)
    print(f"PDF generated: {pdf_path}")

if __name__ == '__main__':
    # Example usage with backaddress auto-generated
    main(
        from_name="John Doe",
        from_address="123 Main Street\nCity, Country",
        recipient_name="Jane Smith",
        recipient_address="456 Another Street\nCity, Country",
        opening="Dear Jane,",
        body="This is a sample letter created with auto-generated backaddress.",
        closing="Sincerely, John Doe"
    )
