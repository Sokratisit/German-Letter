from __future__ import annotations

import re
import subprocess
import tempfile
from datetime import date
from pathlib import Path

from .validation import LetterFormData


class LatexBuildError(RuntimeError):
    """Raised when the LaTeX build process fails."""


LATEX_ESCAPES: dict[str, str] = {
    "\\": r"\textbackslash{}",
    "&": r"\&",
    "%": r"\%",
    "$": r"\$",
    "#": r"\#",
    "_": r"\_",
    "{": r"\{",
    "}": r"\}",
    "~": r"\textasciitilde{}",
    "^": r"\textasciicircum{}",
}


def escape_latex(text: str) -> str:
    return "".join(LATEX_ESCAPES.get(char, char) for char in text)


def format_german_date(value: date) -> str:
    return f"{value.day}.{value.month}.{value.year}"


def _latex_lines(text: str) -> str:
    paragraphs = []
    for paragraph in re.split(r"(?:\r?\n)\s*(?:\r?\n)+", text):
        lines = [escape_latex(line.strip()) for line in paragraph.splitlines()]
        lines = [line for line in lines if line]
        if lines:
            paragraphs.append(r"\\ ".join(lines))

    if not paragraphs:
        return ""
    return "\n\n".join(paragraphs)


def _address_lines(*parts: str) -> str:
    lines = [escape_latex(part) for part in parts if part]
    return r"\\ ".join(lines)


def _recipient_name(data: LetterFormData) -> str:
    return data.recipient_display_name


def _recipient_address_lines(data: LetterFormData) -> str:
    return _address_lines(
        _recipient_name(data),
        data.recipient_extra,
        _join_non_empty((data.recipient_street, data.recipient_street_number)),
        _join_non_empty((data.recipient_postal_code, data.recipient_city)),
    )


def _sender_address_lines(data: LetterFormData) -> str:
    return _address_lines(
        data.sender_extra,
        _join_non_empty((data.sender_street, data.sender_street_number)),
        _join_non_empty((data.sender_postal_code, data.sender_city)),
    )


def _backaddress_text(data: LetterFormData) -> str:
    separator = data.sender_backaddress_separator or ", "
    parts = [
        _abbreviated_name(data.sender_title, data.sender_first_name, data.sender_last_name),
        data.sender_extra,
        _join_non_empty((data.sender_street, data.sender_street_number)),
        _join_non_empty((data.sender_postal_code, data.sender_city)),
    ]
    cleaned_parts = [escape_latex(part) for part in parts if part]
    return separator.join(cleaned_parts)


def _abbreviated_name(title: str, first_name: str, last_name: str) -> str:
    initials = [f"{part[0]}." for part in first_name.split() if part]
    parts = [title, *initials, last_name]
    return " ".join(part for part in parts if part).strip()


def _join_non_empty(values: tuple[str, ...]) -> str:
    return " ".join(value for value in values if value)


def _option_bool(value: str) -> str:
    return "true" if value else "false"


def build_letter_tex(data: LetterFormData) -> str:
    sender_line = _sender_address_lines(data)
    recipient_line = _recipient_address_lines(data)
    body = _latex_lines(data.body)
    body_block = body if body else escape_latex(data.body)
    sender_bank = _latex_lines(data.sender_bank)
    subject_separator = data.subject_separator or ": "
    place_separator = data.place_separator or ", "

    koma_options = ",".join(
        (
            "parskip=half",
            "subject=beforeopening",
            "subject=titled",
            f"fromphone={_option_bool(data.sender_phone)}",
            f"frommobilephone={_option_bool(data.sender_mobile_phone)}",
            f"fromfax={_option_bool(data.sender_fax)}",
            f"fromemail={_option_bool(data.sender_email)}",
            f"fromurl={_option_bool(data.sender_url)}",
            f"fromlogo={_option_bool(data.sender_logo)}",
        )
    )

    lines = [
        r"\documentclass[paper=a4,fontsize=11pt]{scrlttr2}",
        rf"\KOMAoptions{{{koma_options}}}",
        r"\setlength{\parindent}{0pt}",
        rf"\setkomavar{{fromname}}{{{escape_latex(data.sender_display_name)}}}",
        rf"\setkomavar{{fromaddress}}{{{sender_line}}}",
        rf"\setkomavar{{backaddressseparator}}{{{escape_latex(data.sender_backaddress_separator or ', ')}}}",
        rf"\setkomavar{{backaddress}}{{{_backaddress_text(data)}}}",
        rf"\setkomavar{{signature}}{{{escape_latex(data.signature)}}}",
        r"\setkomavar*{fromphone}{Telefon: }",
        r"\setkomavar*{frommobilephone}{Mobiltelefon: }",
        r"\setkomavar*{fromfax}{Fax: }",
        r"\setkomavar*{fromemail}{E-Mail: }",
        r"\setkomavar*{fromurl}{URL: }",
        r"\setkomavar*{subject}{Betreff: }",
        rf"\setkomavar{{subject}}{{{escape_latex(data.subject)}}}",
        rf"\setkomavar{{title}}{{{escape_latex(data.letter_title)}}}",
        rf"\setkomavar{{subjectseparator}}{{{escape_latex(subject_separator)}}}",
        r"\setkomavar*{yourref}{Ihr Zeichen}",
        rf"\setkomavar{{yourref}}{{{escape_latex(data.your_reference)}}}",
        r"\setkomavar*{yourmail}{Ihr Schreiben vom}",
        rf"\setkomavar{{yourmail}}{{{escape_latex(data.your_mail)}}}",
        r"\setkomavar*{myref}{Mein Zeichen}",
        rf"\setkomavar{{myref}}{{{escape_latex(data.my_reference)}}}",
        r"\setkomavar*{customer}{Kundennummer}",
        rf"\setkomavar{{customer}}{{{escape_latex(data.customer)}}}",
        r"\setkomavar*{invoice}{Rechnungsnummer}",
        rf"\setkomavar{{invoice}}{{{escape_latex(data.invoice)}}}",
        r"\setkomavar{place}{}",
        rf"\setkomavar{{placeseparator}}{{{escape_latex(place_separator)}}}",
        rf"\setkomavar{{date}}{{{_date_line_latex(data.place, place_separator, data.date_iso)}}}",
        r"\setkomavar*{date}{Datum}",
        rf"\setkomavar{{toname}}{{{escape_latex(_recipient_name(data))}}}",
        rf"\setkomavar{{toaddress}}{{{recipient_line}}}",
        rf"\setkomavar{{fromphone}}{{{escape_latex(data.sender_phone)}}}",
        rf"\setkomavar{{frommobilephone}}{{{escape_latex(data.sender_mobile_phone)}}}",
        rf"\setkomavar{{fromfax}}{{{escape_latex(data.sender_fax)}}}",
        rf"\setkomavar{{fromemail}}{{{escape_latex(data.sender_email)}}}",
        rf"\setkomavar{{fromurl}}{{{escape_latex(data.sender_url)}}}",
        rf"\setkomavar{{frombank}}{{{sender_bank}}}",
    ]

    if data.sender_logo:
        lines.append(r"\setkomavar{fromlogo}{" + data.sender_logo + "}")

    lines.extend(
        (
            r"\begin{document}",
            r"\begin{letter}{" + recipient_line + "}",
            r"\opening{" + _nonempty_letter_field(data.opening) + "}",
            body_block,
            r"\closing{" + escape_latex(data.closing) + "}",
        )
    )

    if data.ps:
        lines.append(r"\ps " + escape_latex(data.ps))
    if data.encl:
        lines.append(_labeled_block("Anlagen", data.encl_separator, data.encl))
    if data.cc:
        lines.append(_labeled_block("Verteiler", data.cc_separator, data.cc))

    lines.extend((r"\end{letter}", r"\end{document}"))
    return "\n".join(lines) + "\n"


def write_tex_file(content: str, destination: Path) -> Path:
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(content, encoding="utf-8")
    return destination


def _cleanup_auxiliary_files(stem: Path) -> None:
    for suffix in (".aux", ".log", ".out", ".tex"):
        aux_path = stem.with_suffix(suffix)
        if aux_path.exists():
            aux_path.unlink()


def build_output_filename(data: LetterFormData) -> str:
    addressee = _sanitize_filename_component(data.filename_addressee)
    return f"{data.date_iso.isoformat()} {addressee}.pdf"


def _sanitize_filename_component(value: str) -> str:
    sanitized = re.sub(r'[<>:"/\\\\|?*]+', " ", value).strip()
    sanitized = re.sub(r"\s+", " ", sanitized)
    return sanitized.rstrip(".") or "Empfänger"


def render_letter_pdf(data: LetterFormData, *, pdflatex_bin: str = "pdflatex") -> tuple[str, bytes]:
    output_filename = build_output_filename(data)
    with tempfile.TemporaryDirectory(prefix="letter-app-") as tmp_name:
        tmp_dir = Path(tmp_name)
        stem = tmp_dir / "letter"
        tex_path = write_tex_file(build_letter_tex(data), stem.with_suffix(".tex"))

        cmd = [
            pdflatex_bin,
            "-interaction=nonstopmode",
            "-halt-on-error",
            tex_path.name,
        ]
        result = subprocess.run(
            cmd,
            cwd=tmp_dir,
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode != 0:
            message = (result.stderr or result.stdout).strip()
            raise LatexBuildError(f"LaTeX build failed: {message}")

        pdf_path = stem.with_suffix(".pdf")
        if not pdf_path.exists():
            raise LatexCompileError("Compilation reported success but no PDF was produced.")
        pdf_bytes = pdf_path.read_bytes()
        _cleanup_auxiliary_files(stem)

    return output_filename, pdf_bytes


def generate_letter_pdf(
    data: LetterFormData, *, generated_dir: Path, pdflatex_bin: str = "pdflatex"
) -> Path:
    generated_dir.mkdir(parents=True, exist_ok=True)
    output_filename, pdf_bytes = render_letter_pdf(data, pdflatex_bin=pdflatex_bin)
    output_path = generated_dir / output_filename
    output_path.write_bytes(pdf_bytes)
    return output_path


class LatexCompileError(LatexBuildError):
    pass


def _separator_label(value: str, fallback: str) -> str:
    text = value if value else fallback
    return text if text.endswith(" ") else f"{text} "


def _date_line(place: str, separator: str, value: date) -> str:
    date_text = format_german_date(value)
    if not place:
        return date_text
    return f"{place}{separator}{date_text}"


def _date_line_latex(place: str, separator: str, value: date) -> str:
    date_text = escape_latex(format_german_date(value))
    if not place:
        return date_text
    return f"{escape_latex(place)}{_latex_separator(separator)}{date_text}"


def _labeled_block(label: str, separator: str, content: str) -> str:
    content_text = _latex_lines(content)
    if not content_text:
        return ""
    return rf"\par {escape_latex(_label_prefix(label, separator))}{content_text}"


def _label_prefix(label: str, separator: str) -> str:
    effective_separator = separator if separator else ": "
    return f"{label}{effective_separator}"


def _latex_separator(separator: str) -> str:
    text = separator or ""
    parts: list[str] = []
    for char in text:
        if char == " ":
            parts.append("~")
        else:
            parts.append(escape_latex(char))
    return "".join(parts)


def _nonempty_letter_field(value: str) -> str:
    return escape_latex(value) if value else "~"
