# German Letter Generator

German Letter Generator is a Flask web app for composing German letters and generating PDFs with LaTeX `scrlttr2`.

It is intended as a practical letter-writing tool rather than a generic LaTeX editor. The form collects sender, recipient, subject, references, body text, closing, attachments, distribution list, and place/date information, then renders a finished PDF for download in the browser.

## Features

- Web form for German business-style letters
- PDF generation with LaTeX `scrlttr2`
- Main letter body can be authored as Markdown via Pandoc or entered directly as LaTeX
- Browser download of the generated PDF
- Automatic PDF filename preview in the form
- Sender and recipient data can be stored in browser cookies via `Speichern`
- Input validation on the server side
- Temporary LaTeX build files are cleaned up automatically

## Stack

- Python 3.10
- Flask
- LaTeX engine (`lualatex` recommended)
- `uv` for local dependency management
- `pytest`

## Project structure

```text
project/
    main.py
    pyproject.toml
    README.md
    app/
        __init__.py
        latex.py
        routes.py
        settings.py
        validation.py
    static/
        favicon.ico
        form.js
        style.css
    templates/
        index.html
        faq.html
        terms.html
    tests/
        test_latex_escape.py
        test_routes.py
        test_template_generation.py
        test_validation.py
```

## Local development

1. Create the virtual environment with Python 3.10:

   ```bash
   uv venv --python 3.10
   ```

2. Install dependencies:

   ```bash
   uv sync --extra dev
   ```

3. Start the app:

   ```bash
   uv run brief
   ```

   The CLI command remains `brief`, because that is the current Python package entry point defined in `pyproject.toml`.

4. Open:

   ```text
   http://127.0.0.1:51816/
   ```

Optional preflight check for runtime tools:

```bash
uv run brief-healthcheck
```

## Tests

Run the test suite with:

```bash
uv run pytest --basetemp .pytest-tmp
```

Local one-off helper scripts for manual deployment or endpoint testing can be kept in a `testing/` folder. That folder is excluded from Git and is not intended for GitHub or PythonAnywhere deployment.

## Requirements

The application requires Docker for sandboxed LaTeX compilation at runtime.
For Markdown letter bodies, it also requires a working `pandoc` binary.

By default, it looks for:

```text
docker
pandoc
lualatex
```

If necessary, the binary path can be configured with an environment variable.

## Configuration

Supported environment variables:

- `LETTER_APP_SECRET_KEY`
- `LETTER_APP_LATEX_BIN` (default: `lualatex`)
- `LETTER_APP_LATEX_FONT_FAMILY` (default: `TeX Gyre Heros`)
- `LETTER_APP_PDFLATEX_BIN` (legacy fallback variable name)
- `LETTER_APP_PANDOC_BIN`
- `LETTER_APP_LATEX_USE_DOCKER` (default: `true`)
- `LETTER_APP_DOCKER_BIN` (default: `docker`)
- `LETTER_APP_DOCKER_IMAGE` (default: `blang/latex:ctanfull`)
- `LETTER_APP_LATEX_TIMEOUT_SECONDS` (default: `20`)
- `LETTER_APP_MAX_CONTENT_LENGTH`

`LETTER_APP_GENERATED_DIR` still exists in the code for compatibility, but the web app currently delivers PDFs directly as browser downloads instead of storing them permanently on the server.

## Deployment on PythonAnywhere

This project can be deployed on PythonAnywhere as a Flask WSGI app.

Recommended directory layout:

```text
/home/<username>/letter/
```

The project files should live there, while the PythonAnywhere WSGI file remains in `/var/www/...`.

### WSGI file

Use a WSGI file like this:

```python
import sys

project_home = "/home/<username>/letter"
if project_home not in sys.path:
    sys.path.insert(0, project_home)

from main import app as application
```

### Static files

Add this static mapping in the PythonAnywhere web configuration:

- URL: `/static/`
- Directory: `/home/<username>/letter/static`

### Dependencies

Install the dependencies into the PythonAnywhere virtualenv for the web app. If `pdflatex` is missing on the server, PDF generation will not work.

## Updating the server with Git

The intended deployment workflow is Git-based, not manual file upload.

Typical update flow:

1. Commit changes locally.
2. Push them to the remote repository.
3. Open a Bash console on PythonAnywhere.
4. Update the server copy:

   ```bash
   cd /home/<username>/letter
   git pull
   ```

5. If dependencies changed, update the virtualenv there as well.
6. Reload the web app on PythonAnywhere.

This keeps the server in sync without manually uploading individual files.
