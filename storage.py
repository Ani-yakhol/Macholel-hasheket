# -*- coding: utf-8 -*-
"""
שמירה וטעינה של כללים לקובץ JSON תחת תיקיית ההגדרות של המשתמש.
"""
import os
import sys
import json
from typing import List
from rule import Rule

APP_NAME = "VoiceMonitor"


def get_config_dir() -> str:
    """מחזיר את תיקיית ההגדרות המתאימה למערכת ההפעלה (Windows: %APPDATA%)."""
    if sys.platform == "win32":
        base = os.environ.get("APPDATA", os.path.expanduser("~"))
    else:
        base = os.path.expanduser("~/.config")
    path = os.path.join(base, APP_NAME)
    os.makedirs(path, exist_ok=True)
    return path


def get_config_path() -> str:
    return os.path.join(get_config_dir(), "rules.json")


def save_rules(rules: List[Rule]) -> None:
    path = get_config_path()
    data = [r.to_dict() for r in rules]
    tmp_path = path + ".tmp"
    with open(tmp_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    os.replace(tmp_path, path)


def load_rules() -> List[Rule]:
    path = get_config_path()
    if not os.path.exists(path):
        return []
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return [Rule.from_dict(d) for d in data]
    except (json.JSONDecodeError, OSError, TypeError, ValueError):
        return []
