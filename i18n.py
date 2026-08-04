# -*- coding: utf-8 -*-
"""
שכבת תרגום פשוטה. השפה הפעילה נקבעת פעם אחת בעת אתחול היישום (main.py)
לפי ההגדרה השמורה, ומיושמת הן בכיווניות (RTL/LTR) והן בטקסטים.
שינוי שפה דורש הפעלה מחדש של התוכנה כדי שכל החלונות ייבנו מחדש בכיוון הנכון.
"""

_current_lang = "he"

TRANSLATIONS = {
    # --- כללי / General ---
    "app_title": {"he": "מערכת ניטור קול וזיהוי דיבור", "en": "Voice Monitoring & Speech Detection"},
    "settings": {"he": "הגדרות", "en": "Settings"},
    "save": {"he": "שמירה", "en": "Save"},
    "cancel": {"he": "ביטול", "en": "Cancel"},
    "close": {"he": "סגירה", "en": "Close"},
    "delete": {"he": "מחיקה", "en": "Delete"},
    "edit": {"he": "עריכה", "en": "Edit"},
    "error": {"he": "שגיאה", "en": "Error"},
    "done": {"he": "בוצע", "en": "Done"},
    "confirm_deletion": {"he": "אישור מחיקה", "en": "Confirm Deletion"},
    "invalid_value": {"he": "ערך לא תקין", "en": "Invalid Value"},

    # --- חלון ראשי ---
    "mic_group_title": {"he": "מקרופון פעיל לניטור כללי", "en": "Active Microphone for Monitoring"},
    "select_input_device": {"he": "בחירת התקן קלט:", "en": "Select Input Device:"},
    "default_system_device": {"he": "ברירת המחדל של המערכת", "en": "System Default"},
    "current_level": {"he": "עוצמת קול נקלטת כעת:", "en": "Current Input Level:"},
    "status": {"he": "מצב:", "en": "Status:"},
    "status_waiting": {"he": "ממתין לאתחול המיקרופון...", "en": "Waiting for microphone..."},
    "status_listening": {"he": "מאזין למיקרופון...", "en": "Listening to microphone..."},
    "rules_group_title": {"he": "כללי ניטור", "en": "Monitoring Rules"},
    "new_rule": {"he": "כלל חדש", "en": "New Rule"},
    "toggle_enabled": {"he": "הפעלה / השבתה", "en": "Enable / Disable"},
    "footer_note": {
        "he": "התוכנה ממשיכה לפעול ברקע ומוצגת באזור ההתראות (System Tray). "
              "לסגירה מוחלטת יש לבחור 'יציאה' מתפריט סמל המגש.",
        "en": "The app keeps running in the background and appears in the System Tray. "
              "To fully quit, choose 'Exit' from the tray icon menu.",
    },
    "tray_show_window": {"he": "הצגת החלון", "en": "Show Window"},
    "tray_exit": {"he": "יציאה", "en": "Exit"},
    "tray_running_title": {"he": "ממשיך לפעול ברקע", "en": "Still Running in Background"},
    "tray_running_body": {
        "he": "התוכנה ממשיכה לנטר את המיקרופון. לסגירה מלאה יש להשתמש בתפריט סמל המגש.",
        "en": "The app keeps monitoring the microphone. Use the tray icon menu to fully quit.",
    },
    "select_rule_first": {"he": "בחירת כלל", "en": "Select a Rule"},
    "select_rule_first_body": {"he": "יש לבחור כלל מהרשימה תחילה.", "en": "Please select a rule from the list first."},
    "confirm_delete_rule": {"he": "האם למחוק את הכלל '{name}'?", "en": "Delete the rule '{name}'?"},
    "status_enabled": {"he": "פעיל", "en": "enabled"},
    "status_disabled": {"he": "מושבת", "en": "disabled"},

    # --- עורך כלל ---
    "rule_editor_title": {"he": "עריכת כלל", "en": "Edit Rule"},
    "rule_name": {"he": "שם הכלל:", "en": "Rule Name:"},
    "rule_enabled": {"he": "כלל פעיל", "en": "Rule Enabled"},
    "mic_settings_group": {"he": "הגדרות מיקרופון", "en": "Microphone Settings"},
    "input_device": {"he": "התקן קלט:", "en": "Input Device:"},
    "sensitivity": {"he": "רגישות זיהוי דיבור:", "en": "Speech Detection Sensitivity:"},
    "noise_filter": {"he": "עוצמת סינון רעשי רקע:", "en": "Background Noise Filtering:"},
    "condition_group": {"he": "תנאי הפעלה", "en": "Trigger Condition"},
    "threshold": {"he": "סף עוצמת קול לזיהוי:", "en": "Volume Threshold:"},
    "duration_required": {"he": "משך דיבור רציף נדרש (דקות:שניות):", "en": "Required Continuous Speech (mm:ss):"},
    "cooldown": {"he": "זמן המתנה בין הפעלות (דקות:שניות):", "en": "Cooldown Between Triggers (mm:ss):"},
    "action_group": {"he": "פעולה לביצוע", "en": "Action to Perform"},
    "trial_button": {"he": "▶ ניסוי - הרצת הפעולה לדוגמה", "en": "▶ Trial - Run Action Preview"},
    "trial_prefix": {"he": "ניסוי", "en": "Trial"},
    "trial_note": {
        "he": "הניסוי מריץ את הפעולה כפי שהוגדרה כרגע בטופס (גם אם טרם נשמרה). "
              "עבור פעולות כיבוי מחשב / שינה - הניסוי מציג בלבד תצוגה מקדימה בטוחה.",
        "en": "The trial runs the action using the form's current values (even if unsaved). "
              "For shutdown / sleep actions, the trial only shows a safe preview.",
    },

    # --- פעולות ---
    "action_text_alert": {"he": "הצגת הודעת טקסט", "en": "Show Text Alert"},
    "action_image_alert": {"he": "הצגת הודעה עם תמונה מוטמעת", "en": "Show Alert with Embedded Image"},
    "action_run_script": {"he": "הפעלת תוכנה / סקריפט", "en": "Run Program / Script"},
    "action_shutdown": {"he": "כיבוי המחשב", "en": "Shut Down Computer"},
    "action_play_sound": {"he": "ניגון קובץ שמע ברקע", "en": "Play Sound in Background"},
    "action_sleep": {"he": "כניסה למצב שינה", "en": "Enter Sleep Mode"},
    "action_screen_off": {"he": "כיבוי מסך בלבד", "en": "Turn Off Screen Only"},

    "alert_text_label": {"he": "טקסט ההודעה:", "en": "Alert Text:"},
    "alert_image_label": {"he": "תמונה מוטמעת:", "en": "Embedded Image:"},
    "choose_image": {"he": "בחירת תמונה...", "en": "Choose Image..."},
    "clear_image": {"he": "מחיקת תמונה", "en": "Clear Image"},
    "alert_duration_label": {"he": "משך הצגת ההודעה:", "en": "Alert Display Duration:"},
    "alert_position_label": {"he": "מיקום הצגת ההודעה:", "en": "Alert Screen Position:"},
    "alert_closable_label": {"he": "לאפשר למשתמש לסגור את ההודעה (כפתור 'סגור')", "en": "Allow user to close the alert (show 'Close' button)"},

    "pos_top_left": {"he": "למעלה שמאל", "en": "Top Left"},
    "pos_top_center": {"he": "למעלה מרכז", "en": "Top Center"},
    "pos_top_right": {"he": "למעלה ימין", "en": "Top Right"},
    "pos_middle_left": {"he": "אמצע שמאל", "en": "Middle Left"},
    "pos_center": {"he": "מרכז המסך", "en": "Center"},
    "pos_middle_right": {"he": "אמצע ימין", "en": "Middle Right"},
    "pos_bottom_left": {"he": "למטה שמאל", "en": "Bottom Left"},
    "pos_bottom_center": {"he": "למטה מרכז", "en": "Bottom Center"},
    "pos_bottom_right": {"he": "למטה ימין", "en": "Bottom Right"},

    "script_path_label": {"he": "נתיב לתוכנה/סקריפט:", "en": "Program/Script Path:"},
    "choose_file": {"he": "בחירת קובץ...", "en": "Choose File..."},
    "script_args_label": {"he": "פרמטרים (אופציונלי):", "en": "Arguments (optional):"},

    "shutdown_warning": {
        "he": "⚠ שימו לב: כיבוי המחשב הוא פעולה הרסנית שעלולה לגרום לאובדן עבודה "
              "שלא נשמרה, במיוחד אם ההפעלה נגרמת בטעות (למשל רעש מטלוויזיה בחדר סמוך).\n"
              "מומלץ לבדוק תחילה את הכלל עם פעולת הודעת אזהרה, ולהשתמש בכפתור הניסוי, "
              "לפני מעבר לכיבוי בפועל.",
        "en": "⚠ Note: shutting down the computer is destructive and may cause loss of "
              "unsaved work, especially if triggered accidentally (e.g. a TV in the next room).\n"
              "It's recommended to first test the rule with a text-alert action and the "
              "trial button, before switching to an actual shutdown.",
    },
    "shutdown_delay_label": {"he": "זמן חסד לביטול לפני כיבוי בפועל:", "en": "Cancellable Delay Before Shutdown:"},
    "shutdown_confirm_checkbox": {
        "he": "אני מבין/ה שפעולה זו תכבה את המחשב באופן מלא ומאשר/ת את השימוש בה",
        "en": "I understand this will fully shut down the computer and I confirm using it",
    },
    "need_confirmation_title": {"he": "נדרש אישור", "en": "Confirmation Required"},
    "need_confirmation_body": {
        "he": "כדי להשתמש בפעולת כיבוי מחשב יש לסמן את תיבת האישור המפורש בעמוד הגדרות הכיבוי.",
        "en": "To use the shutdown action you must check the explicit confirmation box on the shutdown settings page.",
    },
    "duration_must_be_positive": {"he": "יש להגדיר משך זמן גדול מאפס.", "en": "Duration must be greater than zero."},

    "sound_file_label": {"he": "קובץ שמע:", "en": "Sound File:"},
    "choose_sound": {"he": "בחירת קובץ שמע...", "en": "Choose Sound File..."},
    "loop_checkbox": {"he": "נגן בלולאה (חוזר שוב ושוב)", "en": "Loop playback (repeat continuously)"},
    "volume_label": {"he": "עוצמת ניגון:", "en": "Playback Volume:"},
    "sound_note": {
        "he": "הניגון מתבצע ברקע באמצעות פלט האודיו של המערכת, ולא דרך נגן מדיה גלוי.",
        "en": "Playback happens in the background through the system audio output, not a visible media player.",
    },
    "sleep_note": {
        "he": "המחשב ייכנס למצב שינה (Sleep) - ניתן להעיר אותו בהקשה על מקלדת/עכבר.",
        "en": "The computer will enter Sleep mode - it can be woken with a key press or mouse move.",
    },
    "screen_off_note": {
        "he": "המסך בלבד יכבה (לא כניסה למצב שינה) - ניתן להדליק אותו בהקשה על מקלדת/עכבר.",
        "en": "Only the screen turns off (not sleep mode) - it can be turned back on with a key press or mouse move.",
    },

    # --- הגדרות: לשונית כללי ---
    "tab_general": {"he": "כללי", "en": "General"},
    "tab_password": {"he": "סיסמה", "en": "Password"},
    "tab_about": {"he": "אודות", "en": "About"},
    "language_label": {"he": "שפת התוכנה:", "en": "Application Language:"},
    "language_hebrew": {"he": "עברית", "en": "Hebrew"},
    "language_english": {"he": "אנגלית", "en": "English"},
    "language_restart_note": {
        "he": "שינוי שפה ייכנס לתוקף לאחר הפעלה מחדש של התוכנה.",
        "en": "Language changes take effect after restarting the application.",
    },
    "dark_mode_label": {"he": "מראה כהה (מצב לילה)", "en": "Dark Appearance (Night Mode)"},
    "general_saved": {"he": "ההגדרות נשמרו.", "en": "Settings saved."},

    # --- הגדרות: לשונית סיסמה ---
    "password_status_on": {"he": "סטטוס: הגנת סיסמה פעילה.", "en": "Status: password protection is active."},
    "password_status_off": {"he": "סטטוס: אין סיסמה כעת (כניסה חופשית).", "en": "Status: no password set (free access)."},
    "new_password": {"he": "סיסמה חדשה:", "en": "New Password:"},
    "confirm_password": {"he": "אימות סיסמה:", "en": "Confirm Password:"},
    "set_password_btn": {"he": "קביעת סיסמה", "en": "Set Password"},
    "current_password": {"he": "סיסמה נוכחית:", "en": "Current Password:"},
    "change_password_btn": {"he": "שינוי סיסמה", "en": "Change Password"},
    "delete_password_btn": {"he": "מחיקת סיסמה", "en": "Delete Password"},
    "password_required": {"he": "יש להזין סיסמה.", "en": "Please enter a password."},
    "passwords_mismatch": {"he": "הסיסמאות אינן תואמות.", "en": "Passwords do not match."},
    "password_set_done": {"he": "הסיסמה נקבעה בהצלחה.", "en": "Password set successfully."},
    "password_wrong": {"he": "הסיסמה הנוכחית שגויה.", "en": "Current password is incorrect."},
    "new_password_title": {"he": "סיסמה חדשה", "en": "New Password"},
    "password_updated": {"he": "הסיסמה עודכנה בהצלחה.", "en": "Password updated successfully."},
    "confirm_remove_password": {"he": "האם להסיר את הגנת הסיסמה לחלוטין?", "en": "Remove password protection entirely?"},
    "password_removed": {"he": "הסיסמה הוסרה.", "en": "Password removed."},

    # --- התחברות ---
    "login_protected": {"he": "התוכנה מוגנת בסיסמה", "en": "This application is password-protected"},
    "login_placeholder": {"he": "הזנת סיסמה", "en": "Enter password"},
    "login_btn": {"he": "כניסה", "en": "Log In"},
    "login_wrong": {"he": "סיסמה שגויה, נסו שוב.", "en": "Incorrect password, please try again."},

    # --- אודות ---
    "about_version": {"he": "גרסה", "en": "Version"},
    "about_description": {
        "he": "תוכנה זו מאזינה למיקרופון המחשב, מזהה דיבור אנושי תוך הבחנה מרעשי רקע "
              "קבועים (כגון מאוורר או מזגן), ומפעילה פעולה מותאמת אישית כאשר דיבור "
              "בעוצמה מסוימת נמשך פרק זמן שהוגדר מראש בכלל.",
        "en": "This application listens to the computer's microphone, detects human speech "
              "while distinguishing it from steady background noise (such as a fan or AC "
              "unit), and triggers a custom action when speech at a certain volume persists "
              "for a duration defined in a rule.",
    },
    "about_credits_title": {"he": "קרדיטים - ספריות בשימוש", "en": "Credits - Libraries Used"},
    "about_license_title": {"he": "רישיון הפצה", "en": "Distribution License"},
    "about_license_body": {
        "he": "מאחר שתוכנה זו משתמשת בספריית PyQt6 תחת רישיון GNU GPL v3 (ולא "
              "ברישיון המסחרי החלופי), הפצה של התוכנה (כקובץ הפעלה מקומפל או כקוד "
              "מקור) לצדדים שלישיים כפופה לתנאי רישיון GPL v3 - לרבות החובה "
              "להנגיש את קוד המקור המלא תחת אותו רישיון לכל מי שמקבל את התוכנה. "
              "לשימוש אישי בלבד, ללא הפצה לאחרים, אין מגבלה מיוחדת מעבר לכך.",
        "en": "Since this application uses the PyQt6 library under the GNU GPL v3 license "
              "(rather than the alternative commercial license), distributing the "
              "application (as a compiled executable or as source code) to third parties "
              "is subject to GPL v3 terms - including the obligation to make the full "
              "source code available under the same license to anyone who receives the "
              "software. For personal use only, without distributing to others, there is "
              "no special restriction beyond that.",
    },
    "about_legal_disclaimer": {
        "he": "הערה: האמור לעיל הוא מידע כללי בלבד ואינו מהווה ייעוץ משפטי. אם "
              "בכוונתכם להפיץ את התוכנה באופן מסחרי או רחב היקף, מומלץ להתייעץ עם "
              "עורך דין בנוגע למשמעויות הרישוי המלאות, או לשקול רכישת רישיון מסחרי "
              "ל-PyQt6 מ-Riverbank Computing.",
        "en": "Note: the above is general information only and does not constitute legal "
              "advice. If you intend to distribute the application commercially or at "
              "scale, it's recommended to consult a lawyer regarding the full licensing "
              "implications, or consider purchasing a commercial PyQt6 license from "
              "Riverbank Computing.",
    },
}


def set_language(lang: str) -> None:
    global _current_lang
    _current_lang = lang if lang in ("he", "en") else "he"


def get_language() -> str:
    return _current_lang


def t(key: str, **kwargs) -> str:
    """מחזיר את הטקסט המתורגם עבור המפתח בשפה הפעילה, עם תמיכה ב-.format()."""
    entry = TRANSLATIONS.get(key)
    if entry is None:
        return key
    text = entry.get(_current_lang, entry.get("he", key))
    if kwargs:
        try:
            text = text.format(**kwargs)
        except (KeyError, IndexError):
            pass
    return text
