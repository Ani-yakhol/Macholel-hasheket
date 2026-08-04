# -*- coding: utf-8 -*-
"""חלון עריכת כלל בודד - כל ההגדרות: עוצמה, רגישות, משך זמן ופעולה."""

import copy

from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, QLabel, QLineEdit,
    QSpinBox, QDoubleSpinBox, QSlider, QComboBox, QPushButton, QGroupBox,
    QCheckBox, QFileDialog, QStackedWidget, QWidget, QMessageBox
)

import i18n
from rule import (
    Rule, ACTION_ORDER, get_action_labels, get_position_labels,
    ACTION_TEXT_ALERT, ACTION_IMAGE_ALERT, ACTION_RUN_SCRIPT, ACTION_SHUTDOWN,
    ACTION_PLAY_SOUND, ACTION_SLEEP, ACTION_SCREEN_OFF, POSITION_ORDER,
)
from audio_engine import list_input_devices
from level_meter import LevelMeter
from time_field import MinSecEdit
from style import configure_group_box_alignment


def _is_rtl() -> bool:
    return i18n.get_language() != "en"


class RuleEditorDialog(QDialog):
    def __init__(self, rule: Rule, live_level_provider=None, trial_callback=None, parent=None):
        super().__init__(parent)
        self.setLayoutDirection(Qt.LayoutDirection.RightToLeft if _is_rtl() else Qt.LayoutDirection.LeftToRight)
        self.setWindowTitle(i18n.t("rule_editor_title"))
        self.setMinimumWidth(560)
        self.original_rule = rule
        self.rule = copy.deepcopy(rule)
        self.live_level_provider = live_level_provider
        self.trial_callback = trial_callback

        self._build_ui()
        self._load_from_rule()

        if self.live_level_provider:
            self._meter_timer = QTimer(self)
            self._meter_timer.timeout.connect(self._update_live_meter)
            self._meter_timer.start(100)

    # ---------------------------------------------------------------- UI

    def _build_ui(self):
        layout = QVBoxLayout(self)

        top_row = QHBoxLayout()
        self.name_edit = QLineEdit()
        self.enabled_check = QCheckBox(i18n.t("rule_enabled"))
        top_row.addWidget(QLabel(i18n.t("rule_name")))
        top_row.addWidget(self.name_edit)
        top_row.addWidget(self.enabled_check)
        layout.addLayout(top_row)

        mic_group = QGroupBox(i18n.t("mic_settings_group"))
        configure_group_box_alignment(mic_group, _is_rtl())
        mic_form = QFormLayout(mic_group)

        self.device_combo = QComboBox()
        self.device_combo.addItem(i18n.t("default_system_device"), -1)
        for idx, name in list_input_devices():
            self.device_combo.addItem(name, idx)
        mic_form.addRow(i18n.t("input_device"), self.device_combo)

        self.live_meter = LevelMeter()
        mic_form.addRow(i18n.t("current_level"), self.live_meter)

        self.sensitivity_slider = self._make_slider(0, 100)
        mic_form.addRow(i18n.t("sensitivity"), self.sensitivity_slider)

        self.noise_filter_slider = self._make_slider(0, 100)
        mic_form.addRow(i18n.t("noise_filter"), self.noise_filter_slider)

        layout.addWidget(mic_group)

        cond_group = QGroupBox(i18n.t("condition_group"))
        configure_group_box_alignment(cond_group, _is_rtl())
        cond_form = QFormLayout(cond_group)

        self.threshold_spin = QDoubleSpinBox()
        self.threshold_spin.setRange(-60.0, 0.0)
        self.threshold_spin.setSuffix(" dBFS")
        self.threshold_spin.setSingleStep(1.0)
        self.threshold_spin.valueChanged.connect(
            lambda v: self.live_meter.set_threshold(v)
        )
        cond_form.addRow(i18n.t("threshold"), self.threshold_spin)

        self.duration_edit = MinSecEdit()
        cond_form.addRow(i18n.t("duration_required"), self.duration_edit)

        self.cooldown_edit = MinSecEdit()
        cond_form.addRow(i18n.t("cooldown"), self.cooldown_edit)

        layout.addWidget(cond_group)

        action_group = QGroupBox(i18n.t("action_group"))
        configure_group_box_alignment(action_group, _is_rtl())
        action_layout = QVBoxLayout(action_group)

        self.action_labels = get_action_labels()
        self.action_combo = QComboBox()
        for key in ACTION_ORDER:
            self.action_combo.addItem(self.action_labels[key], key)
        self.action_combo.currentIndexChanged.connect(self._on_action_changed)
        action_layout.addWidget(self.action_combo)

        self._page_index = {}
        self.action_stack = QStackedWidget()
        for i, key in enumerate(ACTION_ORDER):
            self._page_index[key] = i
            self.action_stack.addWidget(self._build_page_for(key))
        action_layout.addWidget(self.action_stack)

        trial_row = QHBoxLayout()
        trial_row.addStretch()
        self.trial_btn = QPushButton(i18n.t("trial_button"))
        self.trial_btn.setObjectName("flatIconButton")
        self.trial_btn.clicked.connect(self._on_trial_clicked)
        trial_row.addWidget(self.trial_btn)
        action_layout.addLayout(trial_row)

        trial_note = QLabel(i18n.t("trial_note"))
        trial_note.setWordWrap(True)
        trial_note.setStyleSheet("color: #888; font-size: 10px;")
        action_layout.addWidget(trial_note)

        layout.addWidget(action_group)

        btn_row = QHBoxLayout()
        save_btn = QPushButton(i18n.t("save"))
        save_btn.clicked.connect(self._on_save)
        cancel_btn = QPushButton(i18n.t("cancel"))
        cancel_btn.clicked.connect(self.reject)
        btn_row.addStretch()
        btn_row.addWidget(save_btn)
        btn_row.addWidget(cancel_btn)
        layout.addLayout(btn_row)

    def _make_slider(self, lo, hi):
        s = QSlider(Qt.Orientation.Horizontal)
        s.setRange(lo, hi)
        return s

    def _build_page_for(self, key: str) -> QWidget:
        if key in (ACTION_TEXT_ALERT, ACTION_IMAGE_ALERT):
            return self._build_alert_page(with_image=(key == ACTION_IMAGE_ALERT))
        if key == ACTION_RUN_SCRIPT:
            return self._build_script_page()
        if key == ACTION_PLAY_SOUND:
            return self._build_sound_page()
        if key == ACTION_SHUTDOWN:
            return self._build_shutdown_page()
        if key == ACTION_SLEEP:
            return self._build_note_page(i18n.t("sleep_note"))
        if key == ACTION_SCREEN_OFF:
            return self._build_note_page(i18n.t("screen_off_note"))
        return QWidget()

    def _build_note_page(self, text: str) -> QWidget:
        w = QWidget()
        layout = QVBoxLayout(w)
        label = QLabel(text)
        label.setWordWrap(True)
        label.setStyleSheet("color: #555;")
        layout.addWidget(label)
        return w

    def _build_alert_page(self, with_image: bool) -> QWidget:
        w = QWidget()
        form = QFormLayout(w)

        suffix = "img" if with_image else "txt"

        text_edit = QLineEdit()
        form.addRow(i18n.t("alert_text_label"), text_edit)
        setattr(self, f"alert_text_edit_{suffix}", text_edit)

        if with_image:
            img_row = QHBoxLayout()
            self.alert_image_edit = QLineEdit()
            self.alert_image_edit.setReadOnly(True)
            img_btn = QPushButton(i18n.t("choose_image"))
            img_btn.clicked.connect(self._pick_image)
            clear_btn = QPushButton(i18n.t("clear_image"))
            clear_btn.setObjectName("flatIconButton")
            clear_btn.clicked.connect(lambda: self.alert_image_edit.clear())
            img_row.addWidget(self.alert_image_edit)
            img_row.addWidget(img_btn)
            img_row.addWidget(clear_btn)
            form.addRow(i18n.t("alert_image_label"), img_row)

        duration_spin = QDoubleSpinBox()
        duration_spin.setRange(0, 600)
        duration_spin.setSuffix(" s")
        form.addRow(i18n.t("alert_duration_label"), duration_spin)
        setattr(self, f"alert_duration_spin_{suffix}", duration_spin)

        position_combo = QComboBox()
        self.position_labels = get_position_labels()
        for pos_key in POSITION_ORDER:
            position_combo.addItem(self.position_labels[pos_key], pos_key)
        form.addRow(i18n.t("alert_position_label"), position_combo)
        setattr(self, f"alert_position_combo_{suffix}", position_combo)

        closable_check = QCheckBox(i18n.t("alert_closable_label"))
        form.addRow("", closable_check)
        setattr(self, f"alert_closable_check_{suffix}", closable_check)

        return w

    def _build_script_page(self) -> QWidget:
        w = QWidget()
        form = QFormLayout(w)
        path_row = QHBoxLayout()
        self.script_path_edit = QLineEdit()
        self.script_path_edit.setReadOnly(True)
        pick_btn = QPushButton(i18n.t("choose_file"))
        pick_btn.clicked.connect(self._pick_script)
        path_row.addWidget(self.script_path_edit)
        path_row.addWidget(pick_btn)
        form.addRow(i18n.t("script_path_label"), path_row)

        self.script_args_edit = QLineEdit()
        form.addRow(i18n.t("script_args_label"), self.script_args_edit)
        return w

    def _build_shutdown_page(self) -> QWidget:
        w = QWidget()
        layout = QVBoxLayout(w)

        warn = QLabel(i18n.t("shutdown_warning"))
        warn.setWordWrap(True)
        warn.setStyleSheet("color: #A33; font-weight: bold;")
        layout.addWidget(warn)

        form = QFormLayout()
        delay_row = QHBoxLayout()
        self.shutdown_delay_spin = QSpinBox()
        self.shutdown_delay_spin.setRange(5, 600)
        self.shutdown_delay_spin.setSuffix(" s")
        delay_row.addWidget(self.shutdown_delay_spin)
        form.addRow(i18n.t("shutdown_delay_label"), delay_row)
        layout.addLayout(form)

        self.shutdown_confirm_check = QCheckBox(i18n.t("shutdown_confirm_checkbox"))
        layout.addWidget(self.shutdown_confirm_check)
        return w

    def _build_sound_page(self) -> QWidget:
        w = QWidget()
        form = QFormLayout(w)

        path_row = QHBoxLayout()
        self.sound_path_edit = QLineEdit()
        self.sound_path_edit.setReadOnly(True)
        pick_btn = QPushButton(i18n.t("choose_sound"))
        pick_btn.clicked.connect(self._pick_sound)
        path_row.addWidget(self.sound_path_edit)
        path_row.addWidget(pick_btn)
        form.addRow(i18n.t("sound_file_label"), path_row)

        self.sound_loop_check = QCheckBox(i18n.t("loop_checkbox"))
        form.addRow("", self.sound_loop_check)

        self.sound_volume_slider = self._make_slider(0, 100)
        form.addRow(i18n.t("volume_label"), self.sound_volume_slider)

        note = QLabel(i18n.t("sound_note"))
        note.setWordWrap(True)
        note.setStyleSheet("color: #777;")
        form.addRow("", note)
        return w

    # --------------------------------------------------------- callbacks

    def _on_action_changed(self, _index):
        key = self.action_combo.currentData()
        self.action_stack.setCurrentIndex(self._page_index.get(key, 0))

    def _pick_image(self):
        path, _ = QFileDialog.getOpenFileName(
            self, i18n.t("choose_image"), "", "Images (*.png *.jpg *.jpeg *.bmp *.gif)"
        )
        if path:
            self.alert_image_edit.setText(path)

    def _pick_script(self):
        path, _ = QFileDialog.getOpenFileName(
            self, i18n.t("choose_file"), "",
            "Executables (*.exe *.py *.bat *.cmd);;All Files (*.*)"
        )
        if path:
            self.script_path_edit.setText(path)

    def _pick_sound(self):
        path, _ = QFileDialog.getOpenFileName(
            self, i18n.t("choose_sound"), "", "Audio Files (*.wav *.mp3 *.flac *.ogg)"
        )
        if path:
            self.sound_path_edit.setText(path)

    def _update_live_meter(self):
        if self.live_level_provider:
            db, _score = self.live_level_provider()
            self.live_meter.set_level(db)

    def _on_trial_clicked(self):
        if not self.trial_callback:
            return
        preview_rule = self._gather_rule_from_form()
        self.trial_callback(preview_rule)

    # -------------------------------------------------------- load/save

    def _load_from_rule(self):
        r = self.rule
        self.name_edit.setText(r.name)
        self.enabled_check.setChecked(r.enabled)

        idx = self.device_combo.findData(r.device_index)
        self.device_combo.setCurrentIndex(idx if idx >= 0 else 0)

        self.sensitivity_slider.setValue(r.sensitivity)
        self.noise_filter_slider.setValue(r.noise_filter)

        self.threshold_spin.setValue(r.threshold_db)
        self.live_meter.set_threshold(r.threshold_db)

        self.duration_edit.set_seconds(r.duration_seconds)
        self.cooldown_edit.set_seconds(r.cooldown_seconds)

        action_idx = self.action_combo.findData(r.action_type)
        self.action_combo.setCurrentIndex(action_idx if action_idx >= 0 else 0)
        self._on_action_changed(action_idx)

        # שני עמודי ההתראה (טקסט/תמונה) חולקים ערכי בסיס משותפים
        for suffix in ("txt", "img"):
            getattr(self, f"alert_text_edit_{suffix}").setText(r.alert_text)
            getattr(self, f"alert_duration_spin_{suffix}").setValue(r.alert_duration_seconds)
            pos_combo = getattr(self, f"alert_position_combo_{suffix}")
            pos_idx = pos_combo.findData(r.alert_position)
            pos_combo.setCurrentIndex(pos_idx if pos_idx >= 0 else 0)
            getattr(self, f"alert_closable_check_{suffix}").setChecked(r.alert_closable)
        self.alert_image_edit.setText(r.alert_image_path)

        self.script_path_edit.setText(r.script_path)
        self.script_args_edit.setText(r.script_args)

        self.shutdown_delay_spin.setValue(r.shutdown_delay_seconds)
        self.shutdown_confirm_check.setChecked(r.shutdown_confirmed)

        self.sound_path_edit.setText(r.sound_path)
        self.sound_loop_check.setChecked(r.sound_loop)
        self.sound_volume_slider.setValue(r.sound_volume)

    def _gather_rule_from_form(self) -> Rule:
        """אוסף את ערכי הטופס לאובייקט Rule, ללא ולידציה (משמש גם לניסוי)."""
        r = copy.deepcopy(self.rule)
        r.name = self.name_edit.text().strip() or "כלל ללא שם"
        r.enabled = self.enabled_check.isChecked()
        r.device_index = self.device_combo.currentData()
        r.sensitivity = self.sensitivity_slider.value()
        r.noise_filter = self.noise_filter_slider.value()
        r.threshold_db = self.threshold_spin.value()
        r.duration_seconds = self.duration_edit.get_seconds()
        r.cooldown_seconds = self.cooldown_edit.get_seconds()
        r.action_type = self.action_combo.currentData()

        # שולפים את שדות ההתראה מהעמוד הרלוונטי לפי סוג הפעולה שנבחר
        suffix = "img" if r.action_type == ACTION_IMAGE_ALERT else "txt"
        r.alert_text = getattr(self, f"alert_text_edit_{suffix}").text()
        r.alert_duration_seconds = getattr(self, f"alert_duration_spin_{suffix}").value()
        r.alert_position = getattr(self, f"alert_position_combo_{suffix}").currentData()
        r.alert_closable = getattr(self, f"alert_closable_check_{suffix}").isChecked()
        r.alert_image_path = self.alert_image_edit.text()

        r.script_path = self.script_path_edit.text()
        r.script_args = self.script_args_edit.text()

        r.shutdown_delay_seconds = self.shutdown_delay_spin.value()
        r.shutdown_confirmed = self.shutdown_confirm_check.isChecked()

        r.sound_path = self.sound_path_edit.text()
        r.sound_loop = self.sound_loop_check.isChecked()
        r.sound_volume = self.sound_volume_slider.value()
        return r

    def _on_save(self):
        r = self._gather_rule_from_form()

        if r.action_type == ACTION_SHUTDOWN and not r.shutdown_confirmed:
            QMessageBox.warning(self, i18n.t("need_confirmation_title"), i18n.t("need_confirmation_body"))
            return

        if r.duration_seconds <= 0:
            QMessageBox.warning(self, i18n.t("invalid_value"), i18n.t("duration_must_be_positive"))
            return

        self.rule = r
        self.accept()

    def get_rule(self) -> Rule:
        return self.rule
