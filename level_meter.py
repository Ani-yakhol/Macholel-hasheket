# -*- coding: utf-8 -*-
"""ווידג'ט מחוון עוצמת קול בזמן אמת."""

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPainter, QColor, QLinearGradient
from PyQt6.QtWidgets import QWidget


class LevelMeter(QWidget):
    """מד עוצמה אופקי הממיר dBFS (בערך -60..0) לתצוגה ויזואלית."""

    MIN_DB = -60.0
    MAX_DB = 0.0

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumHeight(28)
        self.setMinimumWidth(200)
        self._level_db = self.MIN_DB
        self._threshold_db = None  # אם מוגדר, מצויר קו סף

    def set_level(self, db: float):
        self._level_db = max(self.MIN_DB, min(self.MAX_DB, db))
        self.update()

    def set_threshold(self, db):
        self._threshold_db = db
        self.update()

    def _fraction(self, db: float) -> float:
        return (db - self.MIN_DB) / (self.MAX_DB - self.MIN_DB)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        rect = self.rect().adjusted(1, 1, -1, -1)
        painter.setPen(QColor("#C9C9C9"))
        painter.setBrush(QColor("#F0F0F0"))
        painter.drawRoundedRect(rect, 6, 6)

        frac = self._fraction(self._level_db)
        bar_width = int(rect.width() * frac)
        if bar_width > 0:
            gradient = QLinearGradient(rect.left(), 0, rect.right(), 0)
            gradient.setColorAt(0.0, QColor("#4CAF50"))
            gradient.setColorAt(0.7, QColor("#FFC107"))
            gradient.setColorAt(1.0, QColor("#F44336"))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(gradient)
            bar_rect = rect.adjusted(0, 0, -(rect.width() - bar_width), 0)
            painter.drawRoundedRect(bar_rect, 6, 6)

        if self._threshold_db is not None:
            t_frac = self._fraction(self._threshold_db)
            x = rect.left() + int(rect.width() * t_frac)
            painter.setPen(QColor("#333333"))
            painter.drawLine(x, rect.top(), x, rect.bottom())

        painter.end()
