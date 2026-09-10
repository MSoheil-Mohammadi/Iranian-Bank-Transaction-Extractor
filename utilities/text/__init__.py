"""
نرمال‌سازی متن.

این زیرپکیج مجموعه‌ای از توابع کمکی برای یکسان‌سازی متن‌های فارسی
و عربی است؛ به‌ویژه متنی که ممکن است شامل ارقام فارسی/عربی، حروف
عربی جایگزین، نیم‌فاصله‌های نامرئی یا علائم نگارشی غیرASCII باشد.

توابع در چند ماژول جداگانه سازمان‌دهی شده‌اند:

    - digits:      تبدیل ارقام فارسی/عربی + حذف کاراکترهای غیرعددی
    - letters:     یکسان‌سازی حروف عربی با معادل فارسی
    - whitespace:  پاک‌سازی فاصله‌ها و کاراکترهای نامرئی
    - punctuation: یکسان‌سازی علائم نگارشی
    - normalize:   تابع جامع که همهٔ مراحل بالا را ترکیب می‌کند
"""

from .digits import (
    normalize_digits,
    strip_non_alphanumeric,
    strip_non_digits,
)
from .letters import normalize_letters
from .normalize import normalize_text
from .punctuation import normalize_punctuation
from .whitespace import normalize_whitespace

__all__ = [
    # نرمال‌سازی
    "normalize_digits",
    "normalize_letters",
    "normalize_whitespace",
    "normalize_punctuation",
    "normalize_text",
    # پاک‌سازی
    "strip_non_digits",
    "strip_non_alphanumeric",
]