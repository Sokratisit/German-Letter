from __future__ import annotations

import logging
import re
import subprocess
import tempfile
from datetime import date
from pathlib import Path

from .validation import LetterFormData

logger = logging.getLogger(__name__)


class LatexBuildError(RuntimeError):
    """Raised when the LaTeX build process fails."""


class PandocConversionError(RuntimeError):
    """Raised when Markdown to LaTeX conversion fails."""


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
    logger.debug("escape_latex called; text_length=%d", len(text))
    return "".join(LATEX_ESCAPES.get(char, char) for char in text)


def format_german_date(value: date) -> str:
    logger.debug("format_german_date called; value=%s", value.isoformat())
    return f"{value.day}.{value.month}.{value.year}"


def _latex_lines(text: str) -> str:
    logger.debug("_latex_lines called; text_length=%d", len(text))
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
    logger.debug("_address_lines called; part_count=%d", len(parts))
    lines = [escape_latex(part) for part in parts if part]
    return r"\\ ".join(lines)


def _recipient_name(data: LetterFormData) -> str:
    logger.debug("_recipient_name called")
    return data.recipient_display_name


def _recipient_address_lines(data: LetterFormData) -> str:
    logger.debug("_recipient_address_lines called")
    return _address_lines(
        _recipient_name(data),
        data.recipient_extra,
        _join_non_empty((data.recipient_street, data.recipient_street_number)),
        _join_non_empty((data.recipient_postal_code, data.recipient_city)),
    )


def _sender_address_lines(data: LetterFormData) -> str:
    logger.debug("_sender_address_lines called")
    return _address_lines(
        data.sender_extra,
        _join_non_empty((data.sender_street, data.sender_street_number)),
        _join_non_empty((data.sender_postal_code, data.sender_city)),
        *_sender_custom_lines(data),
    )


def _backaddress_text(data: LetterFormData) -> str:
    logger.debug("_backaddress_text called")
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
    logger.debug("_abbreviated_name called")
    initials = [f"{part[0]}." for part in first_name.split() if part]
    parts = [title, *initials, last_name]
    return " ".join(part for part in parts if part).strip()


def _join_non_empty(values: tuple[str, ...]) -> str:
    logger.debug("_join_non_empty called; value_count=%d", len(values))
    return " ".join(value for value in values if value)


def _sender_custom_lines(data: LetterFormData) -> tuple[str, ...]:
    logger.debug("_sender_custom_lines called")
    return tuple(
        line
        for line in (
            _custom_line(data.sender_custom_1_key, data.sender_custom_1_value),
            _custom_line(data.sender_custom_2_key, data.sender_custom_2_value),
            _custom_line(data.sender_custom_3_key, data.sender_custom_3_value),
        )
        if line
    )


def _custom_line(label: str, value: str) -> str:
    logger.debug("_custom_line called")
    if label and value:
        return f"{label}: {value}"
    return label or value


def _option_bool(value: str) -> str:
    logger.debug("_option_bool called; has_value=%s", bool(value))
    return "true" if value else "false"


def convert_markdown_to_latex(markdown_text: str, *, pandoc_bin: str = "pandoc") -> str:
    logger.debug("convert_markdown_to_latex called; markdown_length=%d pandoc_bin=%s", len(markdown_text), pandoc_bin)
    if not markdown_text.strip():
        return ""

    result = subprocess.run(
        [pandoc_bin, "--from=markdown", "--to=latex"],
        input=markdown_text,
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        message = (result.stderr or result.stdout).strip() or "Pandoc conversion failed."
        raise PandocConversionError(f"Markdown conversion failed: {message}")
    return result.stdout.strip()


def _resolve_body_latex(data: LetterFormData, *, pandoc_bin: str) -> str:
    logger.debug("_resolve_body_latex called; body_mode=%s", data.body_mode)
    if data.body_mode == "latex":
        return data.body.strip()
    return convert_markdown_to_latex(data.body, pandoc_bin=pandoc_bin)


def build_letter_tex(data: LetterFormData, *, pandoc_bin: str = "pandoc") -> str:
    logger.debug("build_letter_tex called; body_mode=%s", data.body_mode)
    sender_line = _sender_address_lines(data)
    recipient_line = _recipient_address_lines(data)
    body = _resolve_body_latex(data, pandoc_bin=pandoc_bin)
    body_block = body if body else ""
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
        r"\usepackage[T1]{fontenc}",
        r"\usepackage[utf8]{inputenc}",
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

    lines.extend((r"\begin{document}", r"\begin{letter}{" + recipient_line + "}"))

    if data.opening:
        lines.append(r"\opening{" + escape_latex(data.opening) + "}")
    else:
        lines.append(r"\par")

    lines.extend((body_block, r"\closing{" + escape_latex(data.closing) + "}"))

    if data.ps:
        lines.append(r"\ps " + escape_latex(data.ps))
    if data.encl:
        lines.append(_labeled_block("Anlagen", data.encl_separator, data.encl))
    if data.cc:
        lines.append(_labeled_block("Verteiler", data.cc_separator, data.cc))

    lines.extend((r"\end{letter}", r"\end{document}"))
    return "\n".join(lines) + "\n"


def write_tex_file(content: str, destination: Path) -> Path:
    logger.debug("write_tex_file called; destination=%s", destination)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(content, encoding="utf-8")
    return destination


def _cleanup_auxiliary_files(stem: Path) -> None:
    logger.debug("_cleanup_auxiliary_files called; stem=%s", stem)
    for suffix in (".aux", ".log", ".out", ".tex"):
        aux_path = stem.with_suffix(suffix)
        if aux_path.exists():
            aux_path.unlink()


def build_output_filename(data: LetterFormData) -> str:
    logger.debug("build_output_filename called; has_date=%s", data.date_iso is not None)
    addressee = _sanitize_filename_component(data.filename_addressee)
    if data.date_iso is None:
        return f"{addressee}.pdf"
    return f"{data.date_iso.isoformat()} {addressee}.pdf"


def _sanitize_filename_component(value: str) -> str:
    logger.debug("_sanitize_filename_component called")
    sanitized = re.sub(r'[<>:"/\\\\|?*]+', " ", value).strip()
    sanitized = re.sub(r"\s+", " ", sanitized)
    return sanitized.rstrip(".") or "Empfänger"


def render_letter_pdf(
    data: LetterFormData,
    *,
    pdflatex_bin: str = "pdflatex",
    pandoc_bin: str = "pandoc",
    use_docker: bool = True,
    docker_bin: str = "docker",
    docker_image: str = "blang/latex:ctanfull",
    timeout_seconds: int = 20,
) -> tuple[str, bytes]:
    logger.debug(
        "render_letter_pdf called; use_docker=%s docker_image=%s timeout_seconds=%s",
        use_docker,
        docker_image,
        timeout_seconds,
    )
    output_filename = build_output_filename(data)
    with tempfile.TemporaryDirectory(prefix="letter-app-") as tmp_name:
        tmp_dir = Path(tmp_name)
        stem = tmp_dir / "letter"
        tex_path = write_tex_file(build_letter_tex(data, pandoc_bin=pandoc_bin), stem.with_suffix(".tex"))

        if use_docker:
            result = _run_pdflatex_in_docker(
                tmp_dir=tmp_dir,
                tex_filename=tex_path.name,
                docker_bin=docker_bin,
                docker_image=docker_image,
                timeout_seconds=timeout_seconds,
            )
        else:
            result = _run_pdflatex_locally(
                tmp_dir=tmp_dir,
                tex_filename=tex_path.name,
                pdflatex_bin=pdflatex_bin,
                timeout_seconds=timeout_seconds,
            )
        if result.returncode != 0:
            if use_docker:
                message = _docker_error_message(result.stderr, result.stdout)
            else:
                message = _latex_error_message(result.stderr or result.stdout)
            logger.error("LaTeX build failed; returncode=%s message=%s", result.returncode, message)
            raise LatexBuildError(f"LaTeX build failed: {message}")

        pdf_path = stem.with_suffix(".pdf")
        if not pdf_path.exists():
            raise LatexCompileError("Compilation reported success but no PDF was produced.")
        pdf_bytes = pdf_path.read_bytes()
        _cleanup_auxiliary_files(stem)

    return output_filename, pdf_bytes


class LatexCompileError(LatexBuildError):
    pass


def _run_pdflatex_locally(
    *,
    tmp_dir: Path,
    tex_filename: str,
    pdflatex_bin: str,
    timeout_seconds: int,
):
    logger.debug("_run_pdflatex_locally called; tmp_dir=%s pdflatex_bin=%s", tmp_dir, pdflatex_bin)
    cmd = [
        pdflatex_bin,
        "-interaction=nonstopmode",
        "-halt-on-error",
        tex_filename,
    ]
    try:
        return subprocess.run(
            cmd,
            cwd=tmp_dir,
            capture_output=True,
            text=True,
            check=False,
            timeout=timeout_seconds,
        )
    except subprocess.TimeoutExpired as exc:
        logger.error("Local pdflatex timed out after %ss", timeout_seconds)
        raise LatexBuildError(f"LaTeX build timed out after {timeout_seconds}s.") from exc


def _run_pdflatex_in_docker(
    *,
    tmp_dir: Path,
    tex_filename: str,
    docker_bin: str,
    docker_image: str,
    timeout_seconds: int,
):
    logger.debug("_run_pdflatex_in_docker called; tmp_dir=%s docker_image=%s", tmp_dir, docker_image)
    cmd = [
        docker_bin,
        "run",
        "--rm",
        "--network",
        "none",
        "--read-only",
        "--cap-drop",
        "ALL",
        "--pids-limit",
        "64",
        "--memory",
        "256m",
        "--cpus",
        "0.5",
        "--user",
        "65534:65534",
        "-v",
        f"{tmp_dir}:/work",
        "-w",
        "/work",
        docker_image,
        "pdflatex",
        "-interaction=nonstopmode",
        "-halt-on-error",
        tex_filename,
    ]
    logger.debug("Docker command: %s", " ".join(cmd))
    try:
        return subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=False,
            timeout=timeout_seconds,
        )
    except subprocess.TimeoutExpired as exc:
        logger.error("Docker pdflatex timed out after %ss", timeout_seconds)
        raise LatexBuildError(f"LaTeX build timed out after {timeout_seconds}s.") from exc
    except FileNotFoundError as exc:
        logger.error("Docker binary not found: %s", docker_bin)
        raise LatexBuildError(f"Docker binary not found: {docker_bin}") from exc


def _latex_error_message(raw_output: str) -> str:
    logger.debug("_latex_error_message called; output_length=%d", len(raw_output))
    lines = [line.strip() for line in raw_output.splitlines() if line.strip()]
    if not lines:
        return "Unknown LaTeX error."

    for index, line in enumerate(lines):
        if line.startswith("!"):
            context = [line]
            for extra in lines[index + 1 : index + 3]:
                if extra.startswith("l.") or extra.startswith("<") or extra.startswith("The following"):
                    context.append(extra)
            return " ".join(context)

    return lines[-1]


def _docker_error_message(stderr: str, stdout: str) -> str:
    logger.debug("_docker_error_message called")
    stderr_text = (stderr or "").strip()
    stdout_text = (stdout or "").strip()

    for text in (stderr_text, stdout_text):
        if text:
            lines = [line.strip() for line in text.splitlines() if line.strip()]
            if not lines:
                continue
            if "Run 'docker run --help' for more information" in text and len(lines) >= 2:
                # Prefer the concrete error line before the generic help hint.
                return lines[-2]
            return lines[-1]

    return "Docker run failed without output."


def _separator_label(value: str, fallback: str) -> str:
    logger.debug("_separator_label called")
    text = value if value else fallback
    return text if text.endswith(" ") else f"{text} "


def _date_line_latex(place: str, separator: str, value: date | None) -> str:
    logger.debug("_date_line_latex called; has_date=%s", value is not None)
    if value is None:
        return escape_latex(place) if place else ""
    date_text = escape_latex(format_german_date(value))
    if not place:
        return date_text
    return f"{escape_latex(place)}{_latex_separator(separator)}{date_text}"


def _labeled_block(label: str, separator: str, content: str) -> str:
    logger.debug("_labeled_block called; label=%s", label)
    content_text = _latex_lines(content)
    if not content_text:
        return ""
    return rf"\par {escape_latex(_label_prefix(label, separator))}{content_text}"


def _label_prefix(label: str, separator: str) -> str:
    logger.debug("_label_prefix called; label=%s", label)
    effective_separator = separator if separator else ": "
    return f"{label}{effective_separator}"


def _latex_separator(separator: str) -> str:
    logger.debug("_latex_separator called")
    text = separator or ""
    parts: list[str] = []
    for char in text:
        if char == " ":
            parts.append("~")
        else:
            parts.append(escape_latex(char))
    return "".join(parts)
