# -*- coding: utf-8 -*-
"""
מעקב מצב לכל כלל בנפרד: כמה זמן ברציפות הקול עומד בתנאי הסף,
והפעלת הפעולה המתאימה כאשר מתקיים התנאי למשך הזמן שהוגדר.
"""

import time
from rule import Rule


class RuleState:
    """מצב ריצה (לא נשמר לדיסק) עבור כלל בודד."""

    def __init__(self, rule: Rule):
        self.rule = rule
        self.condition_start_time = None   # מתי התחיל רצף שמקיים את הסף
        self.last_trigger_time = 0.0       # למניעת הפעלות חוזרות (cooldown)
        self.is_currently_active = False   # האם הסף מתקיים כרגע

    def reset(self):
        self.condition_start_time = None
        self.is_currently_active = False

    def update(self, level_db: float, speech_score: float, now: float = None) -> bool:
        """
        מעדכן את מצב הכלל בהתאם למדידה הנוכחית.
        מחזיר True אם יש להפעיל את הפעולה כעת (התנאי התקיים ברציפות
        למשך הזמן הנדרש, וחלף זמן הקירור מההפעלה הקודמת).
        """
        now = now if now is not None else time.time()
        rule = self.rule

        if not rule.enabled:
            self.reset()
            return False

        # ספי "האם זה דיבור": גם עוצמה מספקת וגם ציון דיבוריות מספק
        speech_threshold = 0.45  # קבוע בסיס; מותאם דרך sensitivity בתוך ה-scorer עצמו
        condition_met = level_db >= rule.threshold_db and speech_score >= speech_threshold

        if condition_met:
            if self.condition_start_time is None:
                self.condition_start_time = now
            self.is_currently_active = True

            elapsed = now - self.condition_start_time
            if elapsed >= rule.duration_seconds:
                if now - self.last_trigger_time >= rule.cooldown_seconds:
                    self.last_trigger_time = now
                    return True
        else:
            self.condition_start_time = None
            self.is_currently_active = False

        return False

    def progress_fraction(self, now: float = None) -> float:
        """כמה אחוז מתוך משך הזמן הנדרש כבר חלף (0..1), לתצוגה בממשק."""
        if self.condition_start_time is None or self.rule.duration_seconds <= 0:
            return 0.0
        now = now if now is not None else time.time()
        elapsed = now - self.condition_start_time
        return max(0.0, min(1.0, elapsed / self.rule.duration_seconds))
