# -*- coding: utf-8 -*-
"""
מודל נתונים עבור כלל ניטור קול בודד.
"""
import uuid
from dataclasses import dataclass, field, asdict

import i18n


ACTION_TEXT_ALERT = "text_alert"
ACTION_IMAGE_ALERT = "image_alert"
ACTION_RUN_SCRIPT = "run_script"
ACTION_SHUTDOWN = "shutdown"
ACTION_PLAY_SOUND = "play_sound"
ACTION_SLEEP = "sleep"
ACTION_SCREEN_OFF = "screen_off"

# סדר קבוע לרשימת הפעולות בממשק
ACTION_ORDER = [
    ACTION_TEXT_ALERT,
    ACTION_IMAGE_ALERT,
    ACTION_RUN_SCRIPT,
    ACTION_PLAY_SOUND,
    ACTION_SLEEP,
    ACTION_SCREEN_OFF,
    ACTION_SHUTDOWN,
]

_ACTION_LABEL_KEYS = {
    ACTION_TEXT_ALERT: "action_text_alert",
    ACTION_IMAGE_ALERT: "action_image_alert",
    ACTION_RUN_SCRIPT: "action_run_script",
    ACTION_SHUTDOWN: "action_shutdown",
    ACTION_PLAY_SOUND: "action_play_sound",
    ACTION_SLEEP: "action_sleep",
    ACTION_SCREEN_OFF: "action_screen_off",
}

# תשעת המיקומים האפשריים להצגת הודעת אזהרה על המסך
POSITION_TOP_LEFT = "top_left"
POSITION_TOP_CENTER = "top_center"
POSITION_TOP_RIGHT = "top_right"
POSITION_MIDDLE_LEFT = "middle_left"
POSITION_CENTER = "center"
POSITION_MIDDLE_RIGHT = "middle_right"
POSITION_BOTTOM_LEFT = "bottom_left"
POSITION_BOTTOM_CENTER = "bottom_center"
POSITION_BOTTOM_RIGHT = "bottom_right"

POSITION_ORDER = [
    POSITION_TOP_LEFT, POSITION_TOP_CENTER, POSITION_TOP_RIGHT,
    POSITION_MIDDLE_LEFT, POSITION_CENTER, POSITION_MIDDLE_RIGHT,
    POSITION_BOTTOM_LEFT, POSITION_BOTTOM_CENTER, POSITION_BOTTOM_RIGHT,
]

_POSITION_LABEL_KEYS = {
    POSITION_TOP_LEFT: "pos_top_left",
    POSITION_TOP_CENTER: "pos_top_center",
    POSITION_TOP_RIGHT: "pos_top_right",
    POSITION_MIDDLE_LEFT: "pos_middle_left",
    POSITION_CENTER: "pos_center",
    POSITION_MIDDLE_RIGHT: "pos_middle_right",
    POSITION_BOTTOM_LEFT: "pos_bottom_left",
    POSITION_BOTTOM_CENTER: "pos_bottom_center",
    POSITION_BOTTOM_RIGHT: "pos_bottom_right",
}


def get_action_labels() -> dict:
    """מחזיר מיפוי action_type -> תווית מתורגמת, לפי השפה הפעילה כעת."""
    return {key: i18n.t(label_key) for key, label_key in _ACTION_LABEL_KEYS.items()}


def get_position_labels() -> dict:
    """מחזיר מיפוי position -> תווית מתורגמת, לפי השפה הפעילה כעת."""
    return {key: i18n.t(label_key) for key, label_key in _POSITION_LABEL_KEYS.items()}


@dataclass
class Rule:
    """כלל בודד: תנאי הפעלה (עוצמה+משך+רגישות) ופעולה לביצוע."""

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = "כלל חדש"
    enabled: bool = True

    # --- קלט מקרופון ---
    device_index: int = -1          # -1 = ברירת מחדל של המערכת
    sensitivity: int = 50           # 0-100, רגישות זיהוי דיבור מול רעש
    noise_filter: int = 50          # 0-100, עוצמת סינון רעשי רקע (VAD)

    # --- תנאי הפעלה ---
    threshold_db: float = -25.0     # סף עוצמת קול (dBFS), טווח בערך -60..0
    duration_seconds: float = 3.0   # משך זמן רציף שבו הקול חייב להישמע

    # --- פעולה ---
    action_type: str = ACTION_TEXT_ALERT

    # פרמטרים משותפים להודעות טקסט/תמונה
    alert_text: str = "זוהה דיבור!"
    alert_image_path: str = ""      # נתיב לתמונה מוטמעת (רלוונטי רק ל-image_alert)
    alert_duration_seconds: float = 5.0
    alert_position: str = POSITION_BOTTOM_RIGHT
    alert_closable: bool = False    # ב"מ: לא ניתן לסגור ידנית

    # פרמטרים של הפעלת סקריפט/תוכנה
    script_path: str = ""
    script_args: str = ""

    # פרמטרים של ניגון שמע
    sound_path: str = ""
    sound_loop: bool = False
    sound_volume: int = 100         # 0-100

    # פרמטרים של כיבוי מחשב
    shutdown_confirmed: bool = False   # חובה לאשר באופן מפורש בממשק
    shutdown_delay_seconds: int = 30   # זמן חסד לפני כיבוי בפועל (ניתן לבטל)

    # --- קירור בין הפעלות (כדי שלא יופעל שוב ושוב ברצף) ---
    cooldown_seconds: float = 10.0

    def to_dict(self):
        return asdict(self)

    @staticmethod
    def from_dict(d: dict) -> "Rule":
        valid_keys = Rule.__dataclass_fields__.keys()
        filtered = {k: v for k, v in d.items() if k in valid_keys}
        # תאימות לאחור: כללים ישנים ששמרו action_type="show_alert" הופכים
        # לפעולת הודעת טקסט (או תמונה, אם היה נתיב תמונה מוגדר).
        if filtered.get("action_type") == "show_alert":
            had_image = bool(filtered.get("alert_image_path"))
            filtered["action_type"] = ACTION_IMAGE_ALERT if had_image else ACTION_TEXT_ALERT
        return Rule(**filtered)
