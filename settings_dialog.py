# -*- coding: utf-8 -*-
"""
חלון הגדרות שנפתח מסמל גלגל השיניים: לשונית כללי (שפה/מראה), לשונית
סיסמה, ולשונית אודות/קרדיטים.
"""

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, QLabel, QLineEdit,
    QPushButton, QTabWidget, QWidget, QMessageBox, QTextBrowser, QComboBox,
    QCheckBox
)

import i18n
from app_settings import AppSettings, load_app_settings, save_app_settings
import auth
from version import APP_VERSION, APP_NAME_HE


class SettingsDialog(QDialog):
    def __init__(self, parent=None, on_general_saved=None):
        super().__init__(parent)
        rtl = i18n.get_language() != "en"
        self.setLayoutDirection(Qt.LayoutDirection.RightToLeft if rtl else Qt.LayoutDirection.LeftToRight)
        self.setWindowTitle(i18n.t("settings"))
        self.resize(540, 480)

        self.settings = load_app_settings()
        self.on_general_saved = on_general_saved  # callback(dark_mode:bool) לעדכון תצוגה חיה

        layout = QVBoxLayout(self)
        self.tabs = QTabWidget()
        self.tabs.addTab(self._build_general_tab(), i18n.t("tab_general"))
        self.tabs.addTab(self._build_password_tab(), i18n.t("tab_password"))
        self.tabs.addTab(self._build_about_tab(), i18n.t("tab_about"))
        layout.addWidget(self.tabs)

        close_row = QHBoxLayout()
        close_row.addStretch()
        close_btn = QPushButton(i18n.t("close"))
        close_btn.clicked.connect(self.accept)
        close_row.addWidget(close_btn)
        layout.addLayout(close_row)

    # ---------------------------------------------------------- general

    def _build_general_tab(self) -> QWidget:
        w = QWidget()
        layout = QVBoxLayout(w)
        form = QFormLayout()

        self.language_combo = QComboBox()
        self.language_combo.addItem(i18n.t("language_hebrew"), "he")
        self.language_combo.addItem(i18n.t("language_english"), "en")
        lang_idx = self.language_combo.findData(self.settings.language)
        self.language_combo.setCurrentIndex(lang_idx if lang_idx >= 0 else 0)
        form.addRow(i18n.t("language_label"), self.language_combo)

        layout.addLayout(form)

        restart_note = QLabel(i18n.t("language_restart_note"))
        restart_note.setWordWrap(True)
        restart_note.setStyleSheet("color: #888; font-size: 10px;")
        layout.addWidget(restart_note)

        self.dark_mode_check = QCheckBox(i18n.t("dark_mode_label"))
        self.dark_mode_check.setChecked(self.settings.dark_mode)
        layout.addWidget(self.dark_mode_check)

        save_btn = QPushButton(i18n.t("save"))
        save_btn.clicked.connect(self._on_save_general)
        layout.addWidget(save_btn)

        layout.addStretch()
        return w

    def _on_save_general(self):
        self.settings.language = self.language_combo.currentData()
        self.settings.dark_mode = self.dark_mode_check.isChecked()
        save_app_settings(self.settings)
        if self.on_general_saved:
            self.on_general_saved(self.settings.dark_mode)
        QMessageBox.information(self, i18n.t("done"), i18n.t("general_saved"))

    # --------------------------------------------------------- password

    def _build_password_tab(self) -> QWidget:
        w = QWidget()
        layout = QVBoxLayout(w)

        self.status_label = QLabel()
        layout.addWidget(self.status_label)

        self.set_section = QWidget()
        set_form = QFormLayout(self.set_section)
        self.new_pw_edit = QLineEdit()
        self.new_pw_edit.setEchoMode(QLineEdit.EchoMode.Password)
        self.confirm_pw_edit = QLineEdit()
        self.confirm_pw_edit.setEchoMode(QLineEdit.EchoMode.Password)
        set_form.addRow(i18n.t("new_password"), self.new_pw_edit)
        set_form.addRow(i18n.t("confirm_password"), self.confirm_pw_edit)
        set_btn = QPushButton(i18n.t("set_password_btn"))
        set_btn.clicked.connect(self._on_set_password)
        set_form.addRow("", set_btn)
        layout.addWidget(self.set_section)

        self.manage_section = QWidget()
        manage_layout = QVBoxLayout(self.manage_section)
        manage_layout.setContentsMargins(0, 0, 0, 0)

        verify_form = QFormLayout()
        self.current_pw_edit = QLineEdit()
        self.current_pw_edit.setEchoMode(QLineEdit.EchoMode.Password)
        verify_form.addRow(i18n.t("current_password"), self.current_pw_edit)
        manage_layout.addLayout(verify_form)

        btn_row = QHBoxLayout()
        edit_btn = QPushButton(i18n.t("change_password_btn"))
        edit_btn.clicked.connect(self._on_edit_password)
        delete_btn = QPushButton(i18n.t("delete_password_btn"))
        delete_btn.setObjectName("dangerButton")
        delete_btn.clicked.connect(self._on_delete_password)
        btn_row.addWidget(edit_btn)
        btn_row.addWidget(delete_btn)
        manage_layout.addLayout(btn_row)

        layout.addWidget(self.manage_section)
        layout.addStretch()

        self._refresh_password_section()
        return w

    def _refresh_password_section(self):
        has_password = self.settings.password_enabled and self.settings.password_hash
        if has_password:
            self.status_label.setText(i18n.t("password_status_on"))
            self.set_section.hide()
            self.manage_section.show()
            self.current_pw_edit.clear()
        else:
            self.status_label.setText(i18n.t("password_status_off"))
            self.set_section.show()
            self.manage_section.hide()
            self.new_pw_edit.clear()
            self.confirm_pw_edit.clear()

    def _on_set_password(self):
        pw1 = self.new_pw_edit.text()
        pw2 = self.confirm_pw_edit.text()
        if not pw1:
            QMessageBox.warning(self, i18n.t("error"), i18n.t("password_required"))
            return
        if pw1 != pw2:
            QMessageBox.warning(self, i18n.t("error"), i18n.t("passwords_mismatch"))
            return

        salt = auth.generate_salt()
        self.settings.password_salt = salt
        self.settings.password_hash = auth.hash_password(pw1, salt)
        self.settings.password_enabled = True
        save_app_settings(self.settings)
        QMessageBox.information(self, i18n.t("done"), i18n.t("password_set_done"))
        self._refresh_password_section()

    def _verify_current(self) -> bool:
        current = self.current_pw_edit.text()
        if not auth.verify_password(current, self.settings.password_salt, self.settings.password_hash):
            QMessageBox.warning(self, i18n.t("error"), i18n.t("password_wrong"))
            return False
        return True

    def _on_edit_password(self):
        if not self._verify_current():
            return

        rtl = i18n.get_language() != "en"
        new_dialog = QDialog(self)
        new_dialog.setLayoutDirection(Qt.LayoutDirection.RightToLeft if rtl else Qt.LayoutDirection.LeftToRight)
        new_dialog.setWindowTitle(i18n.t("new_password_title"))
        form = QFormLayout(new_dialog)
        new_edit = QLineEdit(); new_edit.setEchoMode(QLineEdit.EchoMode.Password)
        confirm_edit = QLineEdit(); confirm_edit.setEchoMode(QLineEdit.EchoMode.Password)
        form.addRow(i18n.t("new_password"), new_edit)
        form.addRow(i18n.t("confirm_password"), confirm_edit)
        ok_btn = QPushButton(i18n.t("save"))
        form.addRow("", ok_btn)

        def _save():
            p1, p2 = new_edit.text(), confirm_edit.text()
            if not p1:
                QMessageBox.warning(new_dialog, i18n.t("error"), i18n.t("password_required"))
                return
            if p1 != p2:
                QMessageBox.warning(new_dialog, i18n.t("error"), i18n.t("passwords_mismatch"))
                return
            salt = auth.generate_salt()
            self.settings.password_salt = salt
            self.settings.password_hash = auth.hash_password(p1, salt)
            save_app_settings(self.settings)
            new_dialog.accept()
            QMessageBox.information(self, i18n.t("done"), i18n.t("password_updated"))
            self._refresh_password_section()

        ok_btn.clicked.connect(_save)
        new_dialog.exec()

    def _on_delete_password(self):
        if not self._verify_current():
            return
        confirm = QMessageBox.question(self, i18n.t("confirm_deletion"), i18n.t("confirm_remove_password"))
        if confirm == QMessageBox.StandardButton.Yes:
            self.settings.password_enabled = False
            self.settings.password_salt = ""
            self.settings.password_hash = ""
            save_app_settings(self.settings)
            QMessageBox.information(self, i18n.t("done"), i18n.t("password_removed"))
            self._refresh_password_section()

    # ------------------------------------------------------------ about

    def _build_about_tab(self) -> QWidget:
        w = QWidget()
        layout = QVBoxLayout(w)

        browser = QTextBrowser()
        browser.setOpenExternalLinks(True)
        browser.setHtml(self._about_html())
        layout.addWidget(browser)
        return w

    def _about_html(self) -> str:
        rtl = i18n.get_language() != "en"
        dir_attr = "rtl" if rtl else "ltr"
        return f"""
        <div dir="{dir_attr}" style="font-family: 'Segoe UI'; font-size: 13px; line-height: 1.5;">
        <h3>{i18n.t('app_title')}</h3>
        <p>{i18n.t('about_version')} {APP_VERSION}</p>

        <p>{i18n.t('about_description')}</p>

        <h4>{i18n.t('about_credits_title')}</h4>
        <ul>
        <li><b>Python</b> - PSF License.</li>
        <li><b>PyQt6</b> (Riverbank Computing Ltd.) -
            <b>GNU GPL v3</b> (or an alternative commercial license sold by the vendor).</li>
        <li><b>sounddevice</b> - MIT License.</li>
        <li><b>soundfile</b> - BSD-3-Clause License.</li>
        <li><b>NumPy</b> / <b>SciPy</b> - BSD License.</li>
        </ul>

        <h4>{i18n.t('about_license_title')}</h4>
        <p>{i18n.t('about_license_body')}</p>
        <p style="color:#777;">{i18n.t('about_legal_disclaimer')}</p>
        </div>
        """
