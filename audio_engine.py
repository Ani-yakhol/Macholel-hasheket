# -*- coding: utf-8 -*-
"""
מנוע האזנה למקרופון, חישוב עוצמת קול וזיהוי דיבור (VAD) מול רעשי רקע.

האלגוריתם לזיהוי דיבור (לעומת רעש רקע קבוע כמו מאוורר/מזגן) משלב שלושה מדדים
שמחושבים על כל מסגרת אודיו (frame):

1. עוצמה (RMS -> dBFS) - כמה "חזק" האות.
2. קצב חציית אפס (Zero Crossing Rate) - דיבור אנושי (במיוחד עיצורים) נוטה
   להיות בטווח בינוני-גבוה של ZCR, בעוד רעש לבן קבוע או הום נמוך שונים בעקביות.
3. שטיחות ספקטרלית (Spectral Flatness) - רעש רקע "לבן"/קבוע נוטה להיות שטוח
   יותר בספקטרום (אנרגיה מפוזרת אחידה), בעוד דיבור אנושי הוא "תוצרתי" -
   יש לו מבנה הרמוני ושיאים ברורים (פורמנטים), כך שהשטיחות שלו נמוכה יותר.

המשולב מהם נותן "ציון דיבוריות" (speech score) בין 0 ל-1. הרגישות וסינון
הרעש שמוגדרים בכל כלל קובעים את הסף שמעליו ציון זה נחשב "דיבור".
"""

import threading
import time
import numpy as np

try:
    import sounddevice as sd
except OSError:
    sd = None  # יוגדר כ-None בסביבות ללא PortAudio; הטיפול בשגיאה מתבצע ב-UI

SAMPLE_RATE = 16000
BLOCK_SIZE = 1024  # ~64ms בקצב 16kHz
EPS = 1e-10


def rms_to_dbfs(rms: float) -> float:
    """המרת RMS (0..1) ל-dBFS (שלילי, 0 = מקסימום)."""
    return 20.0 * np.log10(max(rms, EPS))


def compute_zcr(frame: np.ndarray) -> float:
    """קצב חציית אפס מנורמל (0..1)."""
    signs = np.sign(frame)
    signs[signs == 0] = 1
    crossings = np.sum(np.abs(np.diff(signs))) / 2.0
    return crossings / max(len(frame) - 1, 1)


def compute_spectral_flatness(frame: np.ndarray) -> float:
    """
    שטיחות ספקטרלית = יחס ממוצע גיאומטרי לממוצע אריתמטי של ספקטרום ההספק.
    ערך קרוב ל-1 = רעש שטוח (כמו רעש לבן). ערך נמוך = יש מבנה הרמוני (כמו דיבור).
    """
    windowed = frame * np.hanning(len(frame))
    spectrum = np.abs(np.fft.rfft(windowed)) ** 2 + EPS
    log_spec = np.log(spectrum)
    geo_mean = np.exp(np.mean(log_spec))
    arith_mean = np.mean(spectrum)
    return float(geo_mean / max(arith_mean, EPS))


class SpeechScorer:
    """
    מחשב ציון 'דיבוריות' למסגרת אודיו, עם קליברציה אוטומטית של רעש הרקע
    (noise floor) שמתעדכנת לאט כאשר אין דיבור - כך שמזגן/מאוורר קבוע
    "נלמד" כרעש רקע נורמלי ולא מפעיל התראות שווא.
    """

    def __init__(self):
        self.noise_floor_db = -55.0
        self._alpha_noise = 0.02  # קצב התאמת רצפת הרעש (איטי)

    def score(self, frame: np.ndarray, sensitivity_0_100: int, noise_filter_0_100: int):
        rms = float(np.sqrt(np.mean(frame.astype(np.float64) ** 2)))
        db = rms_to_dbfs(rms)
        zcr = compute_zcr(frame)
        flatness = compute_spectral_flatness(frame)

        # נרמול: ZCR בינוני (לא קבוע מדי, לא אפס) -> סביר שזה דיבור
        zcr_score = 1.0 - abs(zcr - 0.12) / 0.12
        zcr_score = float(np.clip(zcr_score, 0.0, 1.0))

        # שטיחות נמוכה = הרמוני יותר = יותר "דיבורי"
        flatness_score = float(np.clip(1.0 - flatness * 4.0, 0.0, 1.0))

        # עוצמה מעל רצפת הרעש הנוכחית
        margin = db - self.noise_floor_db
        level_score = float(np.clip(margin / 30.0, 0.0, 1.0))

        # משקלות: ככל שסינון הרעש (noise_filter) גבוה יותר, נותנים יותר
        # משקל למאפיינים הספקטרליים (ZCR + flatness) ופחות לעוצמה גולמית בלבד
        nf = noise_filter_0_100 / 100.0
        spectral_weight = 0.25 + 0.45 * nf
        level_weight = 1.0 - spectral_weight

        raw_score = (
            level_weight * level_score
            + spectral_weight * 0.5 * zcr_score
            + spectral_weight * 0.5 * flatness_score
        )

        # רגישות מזיזה את סף הפלט (לא רק את החישוב) - רגישות גבוהה = קל יותר להיחשב דיבור
        sens = sensitivity_0_100 / 100.0
        adjusted = float(np.clip(raw_score + (sens - 0.5) * 0.3, 0.0, 1.0))

        # עדכון רצפת רעש רק כשכנראה אין דיבור (ציון נמוך)
        if adjusted < 0.3:
            self.noise_floor_db = (
                (1 - self._alpha_noise) * self.noise_floor_db + self._alpha_noise * db
            )

        return adjusted, db


class AudioEngine(threading.Thread):
    """
    תהליכון רקע שמאזין למקרופון ברציפות, מחשב עוצמה וציון דיבוריות,
    ומפעיל callback בכל בלוק אודיו עם הנתונים העדכניים.
    """

    def __init__(self, device_index=None, on_frame=None, on_error=None):
        super().__init__(daemon=True)
        self.device_index = device_index
        self.on_frame = on_frame      # callback(level_db: float, speech_score: float)
        self.on_error = on_error      # callback(message: str)
        self._stop_event = threading.Event()
        self._scorer = SpeechScorer()
        self._stream = None

    def stop(self):
        self._stop_event.set()

    def run(self):
        if sd is None:
            if self.on_error:
                self.on_error(
                    "ספריית PortAudio לא נמצאה. ודא שהתקנת sounddevice כראוי על Windows."
                )
            return

        def callback(indata, frames, time_info, status):
            if self._stop_event.is_set():
                raise sd.CallbackStop()
            mono = indata[:, 0] if indata.ndim > 1 else indata
            score, db = self._scorer.score(
                mono, sensitivity_0_100=self.sensitivity, noise_filter_0_100=self.noise_filter
            )
            if self.on_frame:
                self.on_frame(db, score)

        # ערכי ברירת מחדל; יעודכנו חיצונית בזמן ריצה ע"י ה-Monitor הראשי
        self.sensitivity = 50
        self.noise_filter = 50

        try:
            with sd.InputStream(
                samplerate=SAMPLE_RATE,
                blocksize=BLOCK_SIZE,
                channels=1,
                dtype="float32",
                device=self.device_index if self.device_index not in (None, -1) else None,
                callback=callback,
            ):
                while not self._stop_event.is_set():
                    time.sleep(0.05)
        except Exception as e:  # noqa: BLE001
            if self.on_error:
                self.on_error(f"שגיאה בגישה למיקרופון: {e}")


def list_input_devices():
    """מחזיר רשימת (index, name) של התקני קלט אודיו זמינים."""
    if sd is None:
        return []
    devices = sd.query_devices()
    result = []
    for idx, dev in enumerate(devices):
        if dev.get("max_input_channels", 0) > 0:
            result.append((idx, dev.get("name", f"התקן {idx}")))
    return result
