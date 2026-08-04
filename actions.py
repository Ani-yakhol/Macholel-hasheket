# -*- coding: utf-8 -*-
"""
ביצוע הפעולות המוגדרות בכלל: הצגת התראת טקסט/תמונה, הפעלת תוכנה/סקריפט,
ניגון קובץ שמע ברקע, כניסה למצב שינה, כיבוי מסך בלבד, או כיבוי המחשב.

הערה לגבי כיבוי מחשב: זוהי פעולה הרסנית (אובדן עבודה לא שמורה) שעלולה
להיגרם מהפעלת שווא של חיישן קול (למשל טלוויזיה בחדר סמוך). לכן הביצוע
מותנה בשני תנאים: (1) המשתמש אישר במפורש בממשק ההגדרות שהוא מבין את
המשמעות, ו-(2) ניתנת חלונית עם ספירה לאחור הניתנת לביטול לפני הכיבוי בפועל,
כדי לתת הזדמנות אחרונה לעצור הפעלה שגויה. כניסה למצב שינה וכיבוי מסך אינן
הרסניות באותה מידה (המחשב אינו נכבה, אין אובדן עבודה), ולכן אינן דורשות
אותה רמת אישור, אך במצב ניסוי הן עדיין מוצגות כתצוגה מקדימה בלבד ולא
מתבצעות בפועל, כדי לא להפתיע את המשתמש באמצע עריכת כלל.
"""

import os
import sys
import subprocess
import threading
import ctypes

from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QObject
from PyQt6.QtGui import QPixmap, QFont
from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout, QPushButton, QHBoxLayout

import i18n
from rule import (
    Rule,
    ACTION_TEXT_ALERT, ACTION_IMAGE_ALERT, ACTION_RUN_SCRIPT, ACTION_SHUTDOWN,
    ACTION_PLAY_SOUND, ACTION_SLEEP, ACTION_SCREEN_OFF,
    POSITION_TOP_LEFT, POSITION_TOP_CENTER, POSITION_TOP_RIGHT,
    POSITION_MIDDLE_LEFT, POSITION_CENTER, POSITION_MIDDLE_RIGHT,
    POSITION_BOTTOM_LEFT, POSITION_BOTTOM_CENTER, POSITION_BOTTOM_RIGHT,
)

try:
    import sounddevice as sd
    import soundfile as sf
except Exception:  # noqa: BLE001
    sd = None
    sf = None


class FloatingAlert(QWidget):
    """
    חלונית הודעה קטנה הצפה מעל שאר החלונות, באחד מתשעה מיקומים אפשריים
    על המסך. ניתן להציג טקסט בלבד או טקסט + תמונה מוטמעת, ולקבוע האם
    יוצג למשתמש כפתור 'סגור' ידני.
    """

    def __init__(
        self,
        text: str,
        image_path: str = "",
        duration_seconds: float = 5.0,
        position: str = POSITION_BOTTOM_RIGHT,
        closable: bool = False,
    ):
        super().__init__()
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.Tool
        )
        self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        self.setStyleSheet(
            """
            QWidget { background-color: #FFF4D6; border: 2px solid #E0A800; border-radius: 10px; }
            QLabel { color: #5A4500; }
            QPushButton {
                background-color: #E0A800; color: white; border-radius: 6px; padding: 4px 10px;
            }
            QPushButton:hover { background-color: #C99400; }
            """
        )

        outer = QVBoxLayout(self)
        outer.setContentsMargins(14, 12, 14, 12)

        if image_path and os.path.exists(image_path):
            img_label = QLabel()
            pix = QPixmap(image_path)
            if not pix.isNull():
                pix = pix.scaledToWidth(220, Qt.TransformationMode.SmoothTransformation)
                img_label.setPixmap(pix)
                img_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                outer.addWidget(img_label)

        text_label = QLabel(text)
        text_label.setWordWrap(True)
        text_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        text_label.setFont(QFont("Segoe UI", 11))
        outer.addWidget(text_label)

        if closable:
            btn_row = QHBoxLayout()
            btn_row.addStretch()
            close_btn = QPushButton(i18n.t("close"))
            close_btn.clicked.connect(self.close)
            btn_row.addWidget(close_btn)
            outer.addLayout(btn_row)

        self.setFixedWidth(280)
        self.adjustSize()
        self._position_on_screen(position)

        if duration_seconds > 0:
            QTimer.singleShot(int(duration_seconds * 1000), self.close)

    def _position_on_screen(self, position: str):
        screen = self.screen().availableGeometry()
        margin = 24
        w, h = self.width(), self.height()

        x_map = {
            "left": screen.left() + margin,
            "center": screen.center().x() - w // 2,
            "right": screen.right() - w - margin,
        }
        y_map = {
            "top": screen.top() + margin,
            "middle": screen.center().y() - h // 2,
            "bottom": screen.bottom() - h - margin,
        }

        parts = {
            POSITION_TOP_LEFT: ("top", "left"),
            POSITION_TOP_CENTER: ("top", "center"),
            POSITION_TOP_RIGHT: ("top", "right"),
            POSITION_MIDDLE_LEFT: ("middle", "left"),
            POSITION_CENTER: ("middle", "center"),
            POSITION_MIDDLE_RIGHT: ("middle", "right"),
            POSITION_BOTTOM_LEFT: ("bottom", "left"),
            POSITION_BOTTOM_CENTER: ("bottom", "center"),
            POSITION_BOTTOM_RIGHT: ("bottom", "right"),
        }
        v_key, h_key = parts.get(position, ("bottom", "right"))
        self.move(x_map[h_key], y_map[v_key])


class ShutdownConfirmWidget(QWidget):
    """
    חלונית ספירה לאחור לפני כיבוי בפועל, עם אפשרות ביטול מיידית.
    כאשר dry_run=True (מצב 'ניסוי' מעורך הכללים) - הספירה לאחור מוצגת
    לצורך התרשמות בלבד, ובתום הזמן הכיבוי האמיתי אינו מתבצע.
    """

    def __init__(self, delay_seconds: int, on_cancel=None, dry_run: bool = False):
        super().__init__()
        self.on_cancel = on_cancel
        self.dry_run = dry_run
        self.remaining = delay_seconds

        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
        )
        self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        self.setStyleSheet(
            """
            QWidget { background-color: #FDEAEA; border: 2px solid #D9534F; border-radius: 10px; }
            QLabel { color: #7A1F1A; }
            QPushButton {
                background-color: #D9534F; color: white; border-radius: 6px; padding: 6px 14px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #C9302C; }
            """
        )

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 14, 16, 14)

        self.label = QLabel()
        self.label.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label.setWordWrap(True)
        layout.addWidget(self.label)

        cancel_btn = QPushButton(i18n.t("cancel"))
        cancel_btn.clicked.connect(self._cancel)
        layout.addWidget(cancel_btn)

        self.setFixedWidth(340)
        self._update_label()
        self.adjustSize()
        self._center()

        self._timer = QTimer(self)
        self._timer.timeout.connect(self._tick)
        self._timer.start(1000)

    def _center(self):
        screen = self.screen().availableGeometry()
        self.move(
            screen.center().x() - self.width() // 2,
            screen.center().y() - self.height() // 2,
        )

    def _update_label(self):
        if self.dry_run:
            self.label.setText(
                f"[{i18n.t('trial_prefix')}] {self.remaining}s"
                if i18n.get_language() == "en"
                else f"[מצב ניסוי] כך תיראה ההתראה - בעוד {self.remaining} שניות"
            )
        else:
            self.label.setText(
                f"Sustained speech detected - shutting down in {self.remaining}s"
                if i18n.get_language() == "en"
                else f"זוהה דיבור ממושך - המחשב יכבה בעוד {self.remaining} שניות"
            )

    def _tick(self):
        self.remaining -= 1
        if self.remaining <= 0:
            self._timer.stop()
            self.close()
            if not self.dry_run:
                _shutdown_now()
        else:
            self._update_label()

    def _cancel(self):
        self._timer.stop()
        if self.on_cancel:
            self.on_cancel()
        self.close()


class PreviewNoticeWidget(QWidget):
    """
    חלונית תצוגה מקדימה פשוטה וקצרה, המשמשת במצב ניסוי לפעולות שאינן
    הרסניות (שינה, כיבוי מסך) - מציגה הודעה בלבד למספר שניות ונעלמת,
    ללא ביצוע הפעולה בפועל.
    """

    def __init__(self, text: str, duration_seconds: float = 2.5):
        super().__init__()
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
        )
        self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        self.setStyleSheet(
            """
            QWidget { background-color: #E8F0FE; border: 2px solid #1976D2; border-radius: 10px; }
            QLabel { color: #0D3C7A; }
            """
        )
        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 16, 18, 16)
        label = QLabel(text)
        label.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setWordWrap(True)
        layout.addWidget(label)

        self.setFixedWidth(340)
        self.adjustSize()
        screen = self.screen().availableGeometry()
        self.move(
            screen.center().x() - self.width() // 2,
            screen.center().y() - self.height() // 2,
        )
        QTimer.singleShot(int(duration_seconds * 1000), self.close)


def _shutdown_now():
    """ביצוע פקודת הכיבוי בפועל (Windows)."""
    if sys.platform == "win32":
        subprocess.run(["shutdown", "/s", "/t", "0"], shell=False)
    else:
        print("[סימולציה] הייתה מתבצעת כעת פקודת כיבוי מחשב (Windows בלבד).")


def _sleep_now():
    """מכניס את המחשב למצב שינה (Windows)."""
    if sys.platform == "win32":
        try:
            ctypes.windll.powrprof.SetSuspendState(False, True, False)
        except Exception as e:  # noqa: BLE001
            print(f"שגיאה בכניסה למצב שינה: {e}")
    else:
        print("[סימולציה] המחשב היה נכנס כעת למצב שינה (Windows בלבד).")


def _screen_off_now():
    """מכבה את המסך בלבד, ללא כניסה למצב שינה (Windows)."""
    if sys.platform == "win32":
        try:
            WM_SYSCOMMAND = 0x0112
            SC_MONITORPOWER = 0xF170
            HWND_BROADCAST = 0xFFFF
            MONITOR_OFF = 2
            ctypes.windll.user32.SendMessageW(
                HWND_BROADCAST, WM_SYSCOMMAND, SC_MONITORPOWER, MONITOR_OFF
            )
        except Exception as e:  # noqa: BLE001
            print(f"שגיאה בכיבוי המסך: {e}")
    else:
        print("[סימולציה] המסך היה נכבה כעת (Windows בלבד).")


def play_sound_background(path: str, loop: bool, volume_0_100: int):
    """מנגן קובץ שמע ברקע ללא תלות בנגן המדיה הדיפולטיבי של המשתמש."""
    if not path or not os.path.exists(path):
        return
    if sd is None or sf is None:
        print("חסרה ספריית soundfile/sounddevice לניגון קובץ שמע.")
        return

    def _worker():
        try:
            data, samplerate = sf.read(path, dtype="float32")
            gain = max(0.0, min(1.0, volume_0_100 / 100.0))
            data = data * gain
            while True:
                sd.play(data, samplerate)
                sd.wait()
                if not loop:
                    break
        except Exception as e:  # noqa: BLE001
            print(f"שגיאה בניגון קובץ שמע: {e}")

    threading.Thread(target=_worker, daemon=True).start()


def run_script(path: str, args: str):
    """מפעיל תוכנה/סקריפט חיצוני."""
    if not path or not os.path.exists(path):
        print("נתיב הסקריפט/תוכנה אינו קיים.")
        return
    try:
        arg_list = args.split() if args else []
        if path.lower().endswith(".py"):
            subprocess.Popen([sys.executable, path] + arg_list)
        else:
            subprocess.Popen([path] + arg_list, shell=False)
    except Exception as e:  # noqa: BLE001
        print(f"שגיאה בהפעלת התוכנה/סקריפט: {e}")


class ActionDispatcher(QObject):
    """
    מבצע פעולות בהתאם להגדרות הכלל. רץ ב-thread הראשי של Qt (חובה
    עבור יצירת חלוניות), ולכן מקבל בקשות דרך signal מתהליכון האודיו.

    dry_run=True משמש למצב 'ניסוי' בעורך הכללים: מריץ את הפעולה לצורך
    התרשמות, אך עבור כיבוי מחשב / שינה / כיבוי מסך - לעולם לא מבצע את
    הפעולה האמיתית במצב זה, אלא מציג תצוגה מקדימה בלבד.
    """

    trigger_signal = pyqtSignal(object, bool)  # מעביר (Rule, dry_run)

    def __init__(self):
        super().__init__()
        self.trigger_signal.connect(self._dispatch)
        self._open_widgets = []  # שמירת רפרנס כדי שלא ייאספו ע"י garbage collector

    def trigger(self, rule: Rule, dry_run: bool = False):
        """נקרא מכל thread; מעביר את הביצוע בבטחה ל-thread הראשי."""
        self.trigger_signal.emit(rule, dry_run)

    def _dispatch(self, rule: Rule, dry_run: bool = False):
        if rule.action_type in (ACTION_TEXT_ALERT, ACTION_IMAGE_ALERT):
            text = rule.alert_text
            if dry_run:
                text = f"[{i18n.t('trial_prefix')}] {text}"
            image_path = rule.alert_image_path if rule.action_type == ACTION_IMAGE_ALERT else ""
            widget = FloatingAlert(
                text=text,
                image_path=image_path,
                duration_seconds=rule.alert_duration_seconds,
                position=rule.alert_position,
                closable=rule.alert_closable,
            )
            widget.show()
            self._open_widgets.append(widget)

        elif rule.action_type == ACTION_RUN_SCRIPT:
            if not dry_run:
                run_script(rule.script_path, rule.script_args)
            else:
                widget = FloatingAlert(
                    text=f"[{i18n.t('trial_prefix')}] {rule.script_path or '(—)'}",
                    duration_seconds=3.0,
                    position=rule.alert_position,
                    closable=True,
                )
                widget.show()
                self._open_widgets.append(widget)

        elif rule.action_type == ACTION_PLAY_SOUND:
            if not dry_run:
                play_sound_background(rule.sound_path, rule.sound_loop, rule.sound_volume)
            else:
                # בניסוי מנגנים פעם אחת בלבד, ללא לולאה, כדי לא "לתקוע" את המשתמש
                play_sound_background(rule.sound_path, False, rule.sound_volume)

        elif rule.action_type == ACTION_SLEEP:
            if dry_run:
                text = (
                    "[Trial] Would enter Sleep mode now" if i18n.get_language() == "en"
                    else "[מצב ניסוי] המחשב היה נכנס כעת למצב שינה"
                )
                widget = PreviewNoticeWidget(text)
                widget.show()
                self._open_widgets.append(widget)
            else:
                _sleep_now()

        elif rule.action_type == ACTION_SCREEN_OFF:
            if dry_run:
                text = (
                    "[Trial] Would turn off the screen now" if i18n.get_language() == "en"
                    else "[מצב ניסוי] המסך היה נכבה כעת"
                )
                widget = PreviewNoticeWidget(text)
                widget.show()
                self._open_widgets.append(widget)
            else:
                _screen_off_now()

        elif rule.action_type == ACTION_SHUTDOWN:
            if dry_run:
                # במצב ניסוי מציגים את חלונית הספירה לאחור לצורך התרשמות בלבד,
                # ולעולם לא מבצעים כיבוי אמיתי - גם אם לא סומנה תיבת האישור.
                widget = ShutdownConfirmWidget(
                    delay_seconds=min(rule.shutdown_delay_seconds, 10), dry_run=True
                )
                widget.show()
                self._open_widgets.append(widget)
                return

            if not rule.shutdown_confirmed:
                # הגנה כפולה: גם אם איכשהו הופעל בלי אישור מפורש בממשק,
                # לא נבצע כיבוי בפועל ללא הסימון המפורש שהמשתמש קבע מראש.
                print("פעולת כיבוי לא תבוצע: לא אושרה במפורש בהגדרות הכלל.")
                return
            widget = ShutdownConfirmWidget(delay_seconds=rule.shutdown_delay_seconds, dry_run=False)
            widget.show()
            self._open_widgets.append(widget)
