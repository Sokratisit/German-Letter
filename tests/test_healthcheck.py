from app.healthcheck import _check_binary


def test_check_binary_reports_success_for_python() -> None:
    ok, detail = _check_binary(["python", "--version"])
    assert ok is True
    assert detail


def test_check_binary_reports_missing_command() -> None:
    ok, detail = _check_binary(["definitely-not-an-existing-command-xyz", "--version"])
    assert ok is False
    assert "not found" in detail
