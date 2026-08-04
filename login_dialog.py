# -*- coding: utf-8 -*-
"""חלון התחברות המוצג בעת הפעלת התוכנה, רק אם הוגדרה סיסמה."""

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton
)

import i18n
from app_settings import AppSettings
import auth


class LoginDialog(QDialog):
    """דורש הזנת סיסמה תקפה לפני שהיישום ייפתח. ניתן לבטל (יציאה מהתוכנה)."""

    def __init__(self, settings: AppSettings, parent=None):
        super().__init__(parent)
        self.settings = settings
        rtl = i18n.get_language() != "en"
        self.setLayoutDirection(Qt.LayoutDirection.RightToLeft if rtl else Qt.LayoutDirection.LeftToRight)
        self.setWindowTitle(i18n.t("app_title"))
        self.setMinimumWidth(360)
        self.setModal(True)

        layout = QVBoxLayout(self)

        title = QLabel(i18n.t("login_protected"))
        title.setStyleSheet("font-weight: bold; font-size: 13px;")
        layout.addWidget(title)

        self.password_edit = QLineEdit()
        self.password_edit.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_edit.setPlaceholderText(i18n.t("login_placeholder"))
        self.password_edit.returnPressed.connect(self._try_login)
        layout.addWidget(self.password_edit)

        self.error_label = QLabel("")
        self.error_label.setStyleSheet("color: #C62828;")
        layout.addWidget(self.error_label)

        btn_row = QHBoxLayout()
        login_btn = QPushButton(i18n.t("login_btn"))
        login_btn.clicked.connect(self._try_login)
        quit_btn = QPushButton(i18n.t("tray_exit"))
        quit_btn.clicked.connect(self.reject)
        btn_row.addStretch()
        btn_row.addWidget(login_btn)
        btn_row.addWidget(quit_btn)
        layout.addLayout(btn_row)

        self.password_edit.setFocus()

    def _try_login(self):
        password = self.password_edit.text()
        if auth.verify_password(password, self.settings.password_salt, self.settings.password_hash):
            self.accept()
        else:
            self.error_label.setText(i18n.t("login_wrong"))
            self.password_edit.clear()
            self.password_edit.setFocus()
