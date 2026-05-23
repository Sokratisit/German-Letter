from app.latex import escape_latex


def test_escape_latex_special_characters() -> None:
    source = "&%$#_{}~^\\"
    expected = (
        r"\&\%\$\#\_\{\}\textasciitilde{}\textasciicircum{}\textbackslash{}"
    )
    assert escape_latex(source) == expected


def test_escape_latex_preserves_plain_text() -> None:
    assert escape_latex("Hallo Welt") == "Hallo Welt"
