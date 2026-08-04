# -*- coding: utf-8 -*-
"""
נקודת הכניסה הראשית לתוכנת ניטור הקול.
הפעלה: python main.py

הערה לגבי שינוי שפה: השפה נטענת פעם אחת כאן, בתחילת ההפעלה, לפני בניית
כל חלון. שינוי שפה בתוך ההגדרות נשמר לדיסק אך נכנס לתוקף רק בהפעלה הבאה
של התוכנה (כפי שגם מצוין למשתמש בממשק) - זאת מכיוון שכיווניות RTL/LTR
היא property שנקבע ברמת ה-QApplication/חלון בעת היצירה ואינו ניתן
להחלפה חלקה תוך כדי ריצה כמו מצב כהה/בהיר.
"""

import sys

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QApplication

import i18n
from main_window import MainWindow
from login_dialog import LoginDialog
from app_settings import load_app_settings
from style import get_stylesheet


def main():
    settings = load_app_settings()
    i18n.set_language(settings.language)
    rtl = settings.language != "en"

    app = QApplication(sys.argv)
    app.setLayoutDirection(Qt.LayoutDirection.RightToLeft if rtl else Qt.LayoutDirection.LeftToRight)
    app.setApplicationName(i18n.t("app_title"))
    app.setQuitOnLastWindowClosed(False)  # התוכנה ממשיכה לרוץ ברקע עם סמל מגש
    app.setStyleSheet(get_stylesheet(dark_mode=settings.dark_mode, rtl=rtl))

    if settings.password_enabled and settings.password_hash:
        login = LoginDialog(settings)
        if login.exec() != LoginDialog.DialogCode.Accepted:
            sys.exit(0)

    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
