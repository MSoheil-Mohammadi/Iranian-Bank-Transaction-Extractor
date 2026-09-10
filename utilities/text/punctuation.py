"""
یکسان‌سازی علائم نگارشی فارسی/عربی با معادل ASCII.

در متن‌های فارسی، علائم نگارشی ممکن است به شکل فارسی/عربی وارد
شوند که کد یونیکد متفاوتی با معادل ASCII دارند. برای مقایسه‌های
رشته‌ای و تطبیق Regex، همه باید به ASCII تبدیل شوند.
"""

from __future__ import annotations

__all__ = ["normalize_punctuation"]

# تبدیل علائم نگارشی فارسی/عربی به معادل ASCII.
_PUNCTUATION_TRANSLATION = str.maketrans({
    "،": ",",  # ویرگول فارسی (U+060C)
    "؛": ";",  # نقطه‌ویرگول فارسی (U+061B)
    "؟": "?",  # علامت سؤال فارسی (U+061F)
    "ـ": "",   # کشیده (U+0640) - حذف می‌شود چون معمولاً تزئینی است
})


def normalize_punctuation(text: str) -> str:
    """یکسان‌سازی علائم نگارشی فارسی/عربی با معادل ASCII.

    Args:
        text: متن ورودی.

    Returns:
        متن با علائم نگارشی ASCII.

    مثال:
        >>> normalize_punctuation("سلام، چطوری؟")
        'سلام, چطوری?'
        >>> normalize_punctuation("بله؛ خوبم")
        'بله; خوبم'
    """
    return text.translate(_PUNCTUATION_TRANSLATION)