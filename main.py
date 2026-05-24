import logging
from pathlib import Path

from app import create_app
from app.healthcheck import run_healthcheck

app = create_app()
_log_file = Path(__file__).resolve().parent / "app.log"
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(_log_file, encoding="utf-8"),
    ],
)
logger = logging.getLogger(__name__)


def main() -> None:
    logger.debug("main called")
    app.run(host="127.0.0.1", port=51816, debug=True)


def healthcheck_main() -> int:
    logger.debug("healthcheck_main called")
    return run_healthcheck()


if __name__ == "__main__":
    main()
