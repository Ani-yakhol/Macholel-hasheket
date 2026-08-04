# -*- coding: utf-8 -*-
"""
פונקציות עזר לגיבוב סיסמה (PBKDF2-HMAC-SHA256 עם salt אקראי).
הסיסמה עצמה אינה נשמרת בשום שלב - רק הגיבוב והמלח.
"""

import os
import hashlib
import binascii

ITERATIONS = 200_000


def generate_salt() -> str:
    return binascii.hexlify(os.urandom(16)).decode("ascii")


def hash_password(password: str, salt_hex: str) -> str:
    salt = binascii.unhexlify(salt_hex)
    dk = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, ITERATIONS)
    return binascii.hexlify(dk).decode("ascii")


def verify_password(password: str, salt_hex: str, expected_hash_hex: str) -> bool:
    if not salt_hex or not expected_hash_hex:
        return False
    candidate = hash_password(password, salt_hex)
    return candidate == expected_hash_hex
