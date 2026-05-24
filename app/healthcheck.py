from __future__ import annotations

import logging
import subprocess

from .settings import AppSettings
logger = logging.getLogger(__name__)


def run_healthcheck(settings: AppSettings | None = None) -> int:
    logger.debug("run_healthcheck called")
    cfg = settings or AppSettings.from_env()
    checks = [
        ("pandoc", _check_binary([cfg.pandoc_bin, "--version"])),
    ]

    if cfg.latex_use_docker:
        checks.append(("docker", _check_binary([cfg.docker_bin, "--version"])))
        checks.append(("docker image", _check_binary([cfg.docker_bin, "image", "inspect", cfg.docker_image])))
    else:
        checks.append(("pdflatex", _check_binary([cfg.pdflatex_bin, "--version"])))

    has_failure = False
    for name, (ok, detail) in checks:
        status = "OK" if ok else "FAIL"
        print(f"[{status}] {name}: {detail}")
        if not ok:
            has_failure = True

    return 1 if has_failure else 0


def _check_binary(cmd: list[str]) -> tuple[bool, str]:
    logger.debug("_check_binary called; cmd=%s", cmd)
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=False,
            timeout=8,
        )
    except FileNotFoundError:
        logger.error("Binary not found: %s", cmd[0])
        return False, f"not found ({cmd[0]})"
    except subprocess.TimeoutExpired:
        logger.error("Command timed out: %s", cmd)
        return False, "timeout"

    if result.returncode != 0:
        output = (result.stderr or result.stdout or "").strip()
        return False, output or f"exit code {result.returncode}"

    output = (result.stdout or result.stderr or "").strip().splitlines()
    return True, output[0] if output else "available"
