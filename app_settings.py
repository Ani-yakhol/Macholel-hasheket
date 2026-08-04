# -*- coding: utf-8 -*-
"""
הגדרות כלליות של היישום (לא קשור לכללי ניטור): כרגע - הגנת סיסמה לכניסה.
נשמר בקובץ נפרד מרשימת הכללים, באותה תיקיית הגדרות.
"""

import os
import json
from dataclasses import dataclass, asdict

import storage


@dataclass
class AppSettings:
    password_enabled: bool = False
    password_salt: str = ""
    password_hash: str = ""
    language: str = "he"        # "he" או "en"
    dark_mode: bool = False

    def to_dict(self):
        return asdict(self)

    @staticmethod
    def from_dict(d: dict) -> "AppSettings":
        valid_keys = AppSettings.__dataclass_fields__.keys()
        filtered = {k: v for k, v in d.items() if k in valid_keys}
        return AppSettings(**filtered)


def get_settings_path() -> str:
    return os.path.join(storage.get_config_dir(), "app_settings.json")


def load_app_settings() -> AppSettings:
    path = get_settings_path()
    if not os.path.exists(path):
        return AppSettings()
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return AppSettings.from_dict(data)
    except (json.JSONDecodeError, OSError, TypeError, ValueError):
        return AppSettings()


def save_app_settings(settings: AppSettings) -> None:
    path = get_settings_path()
    tmp_path = path + ".tmp"
    with open(tmp_path, "w", encoding="utf-8") as f:
        json.dump(settings.to_dict(), f, ensure_ascii=False, indent=2)
    os.replace(tmp_path, path)
