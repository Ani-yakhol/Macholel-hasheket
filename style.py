# -*- coding: utf-8 -*-
"""
מערכת עיצוב מרכזית: מייצרת גיליון QSS בהתאם למראה (בהיר/כהה) ולכיווניות
(RTL/LTR), ומוחלת ברמת QApplication כדי שכל החלונות יקבלו עיצוב אחיד.

תיקון 'אות ראשונה נעלמת' + יישור כותרות ל-RTL:
יש שני חלקים לבעיה. הראשון (מהגרסה הקודמת): מיקום כותרת ה-QGroupBox קרוב
מדי לפינה המעוגלת גרם לחיתוך התו הראשון - תוקן ע"י מרווח (right/left)
מוגדל ורקע מאחורי הכותרת. השני (בקשה נוכחית): גם אם הכותרת לא נחתכת,
היא לא בהכרח "מיושרת" נכון מבחינת יישור טקסט - שכן ל-QGroupBox יש property
נפרד בשם alignment שקובע האם הכותרת צמודה לימין/שמאל/מרכז המסגרת, וברירת
המחדל שלו היא Qt.AlignLeft ללא תלות בכיווניות (RTL/LTR) של שאר הממשק.
משום כך יש לקרוא במפורש ל-setAlignment בכל QGroupBox בהתאם לשפה הנוכחית -
זו מטרת הפונקציה configure_group_box_alignment למטה.
"""

from PyQt6.QtCore import Qt


def _palette(dark: bool) -> dict:
    if dark:
        return {
            "bg": "#1E1E1E",
            "bg_panel": "#2A2A2A",
            "border": "#3D3D3D",
            "text": "#EAEAEA",
            "text_muted": "#9A9A9A",
            "accent": "#2196F3",
            "accent_hover": "#1E88E5",
            "accent_pressed": "#1565C0",
            "danger": "#E57373",
            "danger_hover": "#EF5350",
            "input_bg": "#2A2A2A",
            "tab_bg": "#242424",
        }
    return {
        "bg": "#FAFAFA",
        "bg_panel": "#FFFFFF",
        "border": "#DDDDDD",
        "text": "#222222",
        "text_muted": "#777777",
        "accent": "#1976D2",
        "accent_hover": "#1565C0",
        "accent_pressed": "#0D47A1",
        "danger": "#D9534F",
        "danger_hover": "#C9302C",
        "input_bg": "#FFFFFF",
        "tab_bg": "#F0F0F0",
    }


def get_stylesheet(dark_mode: bool = False, rtl: bool = True) -> str:
    p = _palette(dark_mode)
    title_side = "right" if rtl else "left"

    return f"""
    QMainWindow, QWidget {{
        background-color: {p['bg']};
        color: {p['text']};
    }}
    QDialog {{
        background-color: {p['bg']};
        color: {p['text']};
    }}
    QGroupBox {{
        font-weight: bold;
        border: 1px solid {p['border']};
        border-radius: 8px;
        margin-top: 14px;
        padding-top: 16px;
        background-color: {p['bg_panel']};
    }}
    QGroupBox::title {{
        subcontrol-origin: margin;
        subcontrol-position: top {title_side};
        {title_side}: 18px;
        padding: 1px 8px;
        background-color: {p['bg_panel']};
        border-radius: 4px;
        color: {p['text']};
    }}
    QPushButton {{
        background-color: {p['accent']};
        color: white;
        border-radius: 6px;
        padding: 6px 14px;
        border: none;
    }}
    QPushButton:hover {{ background-color: {p['accent_hover']}; }}
    QPushButton:pressed {{ background-color: {p['accent_pressed']}; }}
    QPushButton:disabled {{ background-color: #999999; color: #DDDDDD; }}

    QPushButton#dangerButton {{ background-color: {p['danger']}; }}
    QPushButton#dangerButton:hover {{ background-color: {p['danger_hover']}; }}

    QPushButton#flatIconButton {{
        background-color: transparent;
        border: 1px solid {p['border']};
        border-radius: 6px;
        padding: 4px 8px;
        color: {p['text']};
    }}
    QPushButton#flatIconButton:hover {{ background-color: {p['bg']}; }}

    QListWidget {{
        border: 1px solid {p['border']};
        border-radius: 6px;
        background-color: {p['bg_panel']};
        color: {p['text']};
    }}
    QLineEdit, QSpinBox, QDoubleSpinBox, QTimeEdit, QComboBox {{
        border: 1px solid {p['border']};
        border-radius: 4px;
        padding: 3px 6px;
        background-color: {p['input_bg']};
        color: {p['text']};
    }}
    QTextBrowser {{
        background-color: {p['bg_panel']};
        color: {p['text']};
        border: 1px solid {p['border']};
        border-radius: 6px;
    }}
    QTabWidget::pane {{
        border: 1px solid {p['border']};
        border-radius: 6px;
        background-color: {p['bg_panel']};
    }}
    QTabBar::tab {{
        background-color: {p['tab_bg']};
        border: 1px solid {p['border']};
        padding: 6px 16px;
        border-top-left-radius: 6px;
        border-top-right-radius: 6px;
        color: {p['text']};
    }}
    QTabBar::tab:selected {{
        background-color: {p['bg_panel']};
        font-weight: bold;
    }}
    QCheckBox {{ spacing: 6px; }}
    QLabel {{ color: {p['text']}; }}
    """


def configure_group_box_alignment(group_box, rtl: bool = True) -> None:
    """
    מיישר במפורש את כותרת ה-QGroupBox לפי כיווניות היישום, מאחר שברירת
    המחדל של Qt לא עוקבת אחרי RTL/LTR באופן אוטומטי עבור property זה.
    """
    group_box.setAlignment(Qt.AlignmentFlag.AlignRight if rtl else Qt.AlignmentFlag.AlignLeft)
