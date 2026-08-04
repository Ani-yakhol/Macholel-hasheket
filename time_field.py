# -*- coding: utf-8 -*-
"""
ווידג'ט הזנת זמן בתבנית דקות:שניות (00:00), עם הקלדה חופשית וחיצי מעלה/מטה
שמעלים שניות ועוברים אוטומטית לדקה הבאה כשחוצים 60 (ולהפך בירידה).

מבוסס על QTimeEdit עם displayFormat="mm:ss" - ה-stepBy המובנה של Qt
מתבסס על חיבור/חיסור שניות אמיתי (QTime.addSecs), ולכן 'גלישה' בין שניות
לדקות מתבצעת אוטומטית וטבעית, בדיוק כמו שעון.
"""

from PyQt6.QtCore import QTime
from PyQt6.QtWidgets import QTimeEdit


class MinSecEdit(QTimeEdit):
    """שדה זמן יחיד בתבנית מ"מ:שש (דקות:שניות), טווח 00:00 עד 59:59."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setDisplayFormat("mm:ss")
        self.setMinimumTime(QTime(0, 0, 0))
        self.setMaximumTime(QTime(0, 59, 59))
        self.setButtonSymbols(QTimeEdit.ButtonSymbols.UpDownArrows)
        self.setWrapping(False)
        self.setAlignment(self._center_alignment())

    @staticmethod
    def _center_alignment():
        from PyQt6.QtCore import Qt
        return Qt.AlignmentFlag.AlignCenter

    def set_seconds(self, total_seconds: float):
        total_seconds = max(0, int(round(total_seconds)))
        minutes = min(59, total_seconds // 60)
        seconds = total_seconds % 60 if total_seconds // 60 <= 59 else 59
        self.setTime(QTime(0, minutes, seconds))

    def get_seconds(self) -> float:
        t = self.time()
        return t.minute() * 60 + t.second()
