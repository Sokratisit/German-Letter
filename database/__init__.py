import json
from functools import partial
from pathlib import Path

from latex import main


def load_configs() -> tuple[dict[str, dict[str, str]], dict[str, dict[str, str]]]:
    """
    Load senders and receivers from a JSON file.

    :return: A tuple of (senders, receivers), where each is a dictionary.
    """
    with open(Path('configs.json'), 'r', encoding='utf-8') as f:
        configs = json.load(f)

    senders = configs.get("sender", {})
    receivers = configs.get("receiver", {})

    return senders, receivers