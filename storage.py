import json
from pathlib import Path

from django.conf import settings


def _path(filename):
    return settings.BASE_DIR / filename


def read_json(filename):
    path = _path(filename)
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


def write_json(filename, data):
    path = _path(filename)
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)
