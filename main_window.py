# -*- coding: utf-8 -*-
"""חלון ראשי: רשימת כללים, מד עוצמה בזמן אמת, בחירת מיקרופון, הגדרות, הפעלה/עצירה."""

import time

from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont, QAction
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QListWidget, QListWidgetItem,
    QPushButton, QLabel, QGroupBox, QFormLayout, QComboBox, QMessageBox,
    QSystemTrayIcon, QMenu, QStyle, QApplication
)

import i18n
from rule import Rule, get_action_labels, ACTION_SHUTDOWN
from rule_state import RuleState
from rule_editor import RuleEditorDialog
from audio_engine import AudioEngine, list_input_devices
from actions import ActionDispatcher
from level_meter import LevelMeter
from settings_dialog import SettingsDialog
from style import get_stylesheet, configure_group_box_alignment
from version import APP_VERSION
import storage


def _is_rtl() -> bool:
    return i18n.get_language() != "en"


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        rtl = _is_rtl()
        self.setLayoutDirection(Qt.LayoutDirection.RightToLeft if rtl else Qt.LayoutDirection.LeftToRight)
        self.setWindowTitle(f"{i18n.t('app_title')}  -  v{APP_VERSION}")
        self.resize(780, 600)

        self.rules = storage.load_rules()
        self.rule_states = {r.id: RuleState(r) for r in self.rules}
        self.dispatcher = ActionDispatcher()

        self.current_db = -60.0
        self.current_score = 0.0
        self.audio_engine = None
        self.selected_device = -1

        self._build_ui()
        self._refresh_rule_list()
        self._init_tray()
        self._start_audio()

        self.ui_timer = QTimer(self)
        self.ui_timer.timeout.connect(self._tick_ui)
        self.ui_timer.start(100)

    # ---------------------------------------------------------------- UI

    def _build_ui(self):
        rtl = _is_rtl()
        central = QWidget()
        self.setCentralWidget(central)
        outer = QVBoxLayout(central)

        # --- שורה עליונה: סמל הגדרות (גלגל שיניים) מוצמד לפינה השמאלית
        # העליונה במפורש, ללא תלות בכיוון RTL הכללי של שאר הממשק ---
        top_bar = QWidget()
        top_bar.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        top_bar_layout = QHBoxLayout(top_bar)
        top_bar_layout.setContentsMargins(0, 0, 0, 0)

        self.settings_btn = QPushButton("⚙")
        self.settings_btn.setObjectName("flatIconButton")
        self.settings_btn.setFixedSize(34, 34)
        self.settings_btn.setToolTip(i18n.t("settings"))
        self.settings_btn.clicked.connect(self._open_settings)
        top_bar_layout.addWidget(self.settings_btn)
        top_bar_layout.addStretch()

        outer.addWidget(top_bar)

        mic_group = QGroupBox(i18n.t("mic_group_title"))
        configure_group_box_alignment(mic_group, rtl)
        mic_form = QFormLayout(mic_group)

        self.device_combo = QComboBox()
        self.device_combo.addItem(i18n.t("default_system_device"), -1)
        for idx, name in list_input_devices():
            self.device_combo.addItem(name, idx)
        self.device_combo.currentIndexChanged.connect(self._on_device_changed)
        mic_form.addRow(i18n.t("select_input_device"), self.device_combo)

        self.global_meter = LevelMeter()
        mic_form.addRow(i18n.t("current_level"), self.global_meter)

        self.status_label = QLabel(i18n.t("status_waiting"))
        self.status_label.setStyleSheet("color: #777;")
        mic_form.addRow(i18n.t("status"), self.status_label)

        outer.addWidget(mic_group)

        rules_group = QGroupBox(i18n.t("rules_group_title"))
        configure_group_box_alignment(rules_group, rtl)
        rules_layout = QVBoxLayout(rules_group)

        self.rule_list = QListWidget()
        self.rule_list.itemDoubleClicked.connect(self._edit_selected_rule)
        rules_layout.addWidget(self.rule_list)

        btn_row = QHBoxLayout()
        add_btn = QPushButton(i18n.t("new_rule"))
        add_btn.clicked.connect(self._add_rule)
        edit_btn = QPushButton(i18n.t("edit"))
        edit_btn.clicked.connect(self._edit_selected_rule)
        del_btn = QPushButton(i18n.t("delete"))
        del_btn.clicked.connect(self._delete_selected_rule)
        toggle_btn = QPushButton(i18n.t("toggle_enabled"))
        toggle_btn.clicked.connect(self._toggle_selected_rule)

        btn_row.addWidget(add_btn)
        btn_row.addWidget(edit_btn)
        btn_row.addWidget(toggle_btn)
        btn_row.addWidget(del_btn)
        rules_layout.addLayout(btn_row)

        outer.addWidget(rules_group)

        footer = QLabel(i18n.t("footer_note"))
        footer.setWordWrap(True)
        footer.setStyleSheet("color: #999; font-size: 11px;")
        outer.addWidget(footer)

        self.setFont(QFont("Segoe UI", 10))

    def _init_tray(self):
        self.tray = QSystemTrayIcon(self)
        icon = self.style().standardIcon(QStyle.StandardPixmap.SP_MediaVolume)
        self.tray.setIcon(icon)
        self.setWindowIcon(icon)

        menu = QMenu()
        show_action = QAction(i18n.t("tray_show_window"), self)
        show_action.triggered.connect(self._show_from_tray)
        quit_action = QAction(i18n.t("tray_exit"), self)
        quit_action.triggered.connect(self._quit_app)
        menu.addAction(show_action)
        menu.addAction(quit_action)
        self.tray.setContextMenu(menu)
        self.tray.activated.connect(
            lambda reason: self._show_from_tray()
            if reason == QSystemTrayIcon.ActivationReason.DoubleClick else None
        )
        self.tray.setToolTip(i18n.t("app_title"))
        self.tray.show()

    def _show_from_tray(self):
        self.showNormal()
        self.activateWindow()

    def _quit_app(self):
        if self.audio_engine:
            self.audio_engine.stop()
        QApplication.quit()

    def closeEvent(self, event):
        event.ignore()
        self.hide()
        self.tray.showMessage(
            i18n.t("tray_running_title"),
            i18n.t("tray_running_body"),
            QSystemTrayIcon.MessageIcon.Information,
            3000,
        )

    def _open_settings(self):
        dialog = SettingsDialog(parent=self, on_general_saved=self._on_theme_changed)
        dialog.exec()

    def _on_theme_changed(self, dark_mode: bool):
        """מיושם מיידית (ללא צורך בהפעלה מחדש) - רק מראה בהיר/כהה; שינוי
        שפה/כיווניות דורש הפעלה מחדש, כפי שמצוין בממשק ההגדרות."""
        app = QApplication.instance()
        if app:
            app.setStyleSheet(get_stylesheet(dark_mode=dark_mode, rtl=_is_rtl()))

    # ------------------------------------------------------------ audio

    def _start_audio(self):
        if self.audio_engine:
            self.audio_engine.stop()
            self.audio_engine.join(timeout=1.0)

        self.audio_engine = AudioEngine(
            device_index=self.selected_device,
            on_frame=self._on_audio_frame,
            on_error=self._on_audio_error,
        )
        self.audio_engine.sensitivity = 50
        self.audio_engine.noise_filter = 50
        self.audio_engine.start()
        self.status_label.setText(i18n.t("status_listening"))
        self.status_label.setStyleSheet("color: #2E7D32;")

    def _on_device_changed(self, _index):
        self.selected_device = self.device_combo.currentData()
        self._start_audio()

    def _on_audio_frame(self, db: float, score: float):
        self.current_db = db
        self.current_score = score

        now = time.time()
        for state in self.rule_states.values():
            if state.update(db, score, now=now):
                self.dispatcher.trigger(state.rule)

    def _on_audio_error(self, message: str):
        self.status_label.setText(message)
        self.status_label.setStyleSheet("color: #C62828;")

    def get_live_level(self):
        return self.current_db, self.current_score

    def run_trial(self, rule: Rule):
        """מריץ פעולה כניסוי מיידי, ללא תלות במצב הכלל השמור (dry_run)."""
        self.dispatcher.trigger(rule, dry_run=True)

    # ------------------------------------------------------------ ticks

    def _tick_ui(self):
        self.global_meter.set_level(self.current_db)

    # -------------------------------------------------------- rule CRUD

    def _refresh_rule_list(self):
        self.rule_list.clear()
        action_labels = get_action_labels()
        for rule in self.rules:
            status = i18n.t("status_enabled") if rule.enabled else i18n.t("status_disabled")
            action_label = action_labels.get(rule.action_type, rule.action_type)
            text = f"{rule.name}  —  {action_label}  —  [{status}]"
            item = QListWidgetItem(text)
            item.setData(Qt.ItemDataRole.UserRole, rule.id)
            if not rule.enabled:
                item.setForeground(Qt.GlobalColor.gray)
            self.rule_list.addItem(item)

    def _selected_rule(self):
        item = self.rule_list.currentItem()
        if not item:
            return None
        rule_id = item.data(Qt.ItemDataRole.UserRole)
        return next((r for r in self.rules if r.id == rule_id), None)

    def _add_rule(self):
        new_rule = Rule(name=f"{i18n.t('new_rule')} {len(self.rules) + 1}")
        dialog = RuleEditorDialog(
            new_rule, live_level_provider=self.get_live_level,
            trial_callback=self.run_trial, parent=self,
        )
        if dialog.exec():
            saved = dialog.get_rule()
            self.rules.append(saved)
            self.rule_states[saved.id] = RuleState(saved)
            self._persist_and_refresh()

    def _edit_selected_rule(self):
        rule = self._selected_rule()
        if not rule:
            QMessageBox.information(self, i18n.t("select_rule_first"), i18n.t("select_rule_first_body"))
            return
        dialog = RuleEditorDialog(
            rule, live_level_provider=self.get_live_level,
            trial_callback=self.run_trial, parent=self,
        )
        if dialog.exec():
            updated = dialog.get_rule()
            idx = next(i for i, r in enumerate(self.rules) if r.id == updated.id)
            self.rules[idx] = updated
            self.rule_states[updated.id] = RuleState(updated)
            self._persist_and_refresh()

    def _delete_selected_rule(self):
        rule = self._selected_rule()
        if not rule:
            return
        confirm = QMessageBox.question(
            self, i18n.t("confirm_deletion"), i18n.t("confirm_delete_rule", name=rule.name)
        )
        if confirm == QMessageBox.StandardButton.Yes:
            self.rules = [r for r in self.rules if r.id != rule.id]
            self.rule_states.pop(rule.id, None)
            self._persist_and_refresh()

    def _toggle_selected_rule(self):
        rule = self._selected_rule()
        if not rule:
            return
        rule.enabled = not rule.enabled
        self._persist_and_refresh()

    def _persist_and_refresh(self):
        storage.save_rules(self.rules)
        self._refresh_rule_list()
