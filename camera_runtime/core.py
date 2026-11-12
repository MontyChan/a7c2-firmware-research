"""Minimal A7C II 2.01 read-only data helpers."""
import hashlib
import io
import re

from .vendor.pmca.backup import BackupFile

MODEL = "ILCE-7CM2"
VERSION = "2.01"
CP_KEYS = (0x02A40001, 0x02A4000D)
RESOURCE_FILES = (
    "string_arabic_horizontal.uxc", "string_arabic_vertical.uxc",
    "string_brazilianportuguese_horizontal.uxc", "string_brazilianportuguese_vertical.uxc",
    "string_bulgarian_horizontal.uxc", "string_bulgarian_vertical.uxc",
    "string_canadianfrench_horizontal.uxc", "string_canadianfrench_vertical.uxc",
    "string_croatian_horizontal.uxc", "string_croatian_vertical.uxc",
    "string_czech_horizontal.uxc", "string_czech_vertical.uxc",
    "string_danish_horizontal.uxc", "string_danish_vertical.uxc",
    "string_dutch_horizontal.uxc", "string_dutch_vertical.uxc",
    "string_english_horizontal.uxc", "string_english_vertical.uxc",
    "string_finnish_horizontal.uxc", "string_finnish_vertical.uxc",
    "string_french_horizontal.uxc", "string_french_vertical.uxc",
    "string_german_horizontal.uxc", "string_german_vertical.uxc",
    "string_greek_horizontal.uxc", "string_greek_vertical.uxc",
    "string_hindi_horizontal.uxc", "string_hindi_vertical.uxc",
    "string_hungarian_horizontal.uxc", "string_hungarian_vertical.uxc",
    "string_indonesia_horizontal.uxc", "string_indonesia_vertical.uxc",
    "string_italian_horizontal.uxc", "string_italian_vertical.uxc",
    "string_japanese_horizontal.uxc", "string_japanese_vertical.uxc",
    "string_korean_horizontal.uxc", "string_korean_vertical.uxc",
    "string_malay_horizontal.uxc", "string_malay_vertical.uxc",
    "string_norwegian_horizontal.uxc", "string_norwegian_vertical.uxc",
    "string_persian_horizontal.uxc", "string_persian_vertical.uxc",
    "string_polish_horizontal.uxc", "string_polish_vertical.uxc",
    "string_portuguese_horizontal.uxc", "string_portuguese_vertical.uxc",
    "string_romanian_horizontal.uxc", "string_romanian_vertical.uxc",
    "string_russian_horizontal.uxc", "string_russian_vertical.uxc",
    "string_simplifiedchinese_horizontal.uxc", "string_simplifiedchinese_vertical.uxc",
    "string_spanish_horizontal.uxc", "string_spanish_vertical.uxc",
    "string_swedish_horizontal.uxc", "string_swedish_vertical.uxc",
    "string_thai_horizontal.uxc", "string_thai_vertical.uxc",
    "string_traditionalchinese_horizontal.uxc", "string_traditionalchinese_vertical.uxc",
    "string_turkish_horizontal.uxc", "string_turkish_vertical.uxc",
    "string_ukrainian_horizontal.uxc", "string_ukrainian_vertical.uxc",
    "string_vietnamese_horizontal.uxc", "string_vietnamese_vertical.uxc",
)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def backup_records(raw):
    """Decode the two BK4 property records from a camera snapshot."""
    result = []
    for match in re.finditer(b"BK4\0", raw):
        try:
            backup = BackupFile(io.BytesIO(raw[match.start() - 12:]))
        except Exception:
            continue
        result.append(dict(backup.listProperties()))
    if len(result) != 2:
        raise ValueError("Camera snapshot must contain two valid BK4 records")
    return result
