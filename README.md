# Brief

Local Flask app for generating German letters as PDF with LaTeX `scrlttr2`.

## Stack

- Flask
- `uv` for dependency and virtualenv management
- HTML/CSS + minimal JavaScript validation
- Server-side validation
- `pytest`

## Project structure

```text
Brief/
    main.py
    app/
        __init__.py
        routes.py
        latex.py
        validation.py
        settings.py
    templates/
        index.html
        result.html
    static/
        style.css
        form.js
    tests/
        test_latex_escape.py
        test_validation.py
        test_template_generation.py
    pyproject.toml
    README.md
```

## Local development

1. Create the root virtualenv with Python 3.10:

   ```bash
   uv venv --python 3.10
   ```

2. Sync dependencies:

   ```bash
   uv sync --extra dev
   ```

3. Run the app:

   ```bash
   uv run brief
   ```

4. Open [http://127.0.0.1:51816/](http://127.0.0.1:51816/).

## Tests

```bash
uv run pytest --basetemp .pytest-tmp
```

## Notes

- Finished PDFs are written to `D:\Users\Admin\Documents\Letter` by default.
- The saved filename format is `YYYY-MM-DD {addressee}.pdf`.
- Temporary LaTeX files are generated in a temp directory and cleaned up after compilation.
- Optional environment variables:
  - `LETTER_APP_SECRET_KEY`
  - `LETTER_APP_GENERATED_DIR`
  - `LETTER_APP_PDFLATEX_BIN`
  - `LETTER_APP_MAX_CONTENT_LENGTH`
