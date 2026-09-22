"""
استخراج و پاک‌سازی شماره سپرده.

شماره سپرده یک شناسهٔ بانکی است که برخلاف شماره کارت (۱۶ رقم با
Luhn) و شبا (۲۶ کاراکتر با Mod 97)، الگوریتم چک‌سام استاندارد
ندارد. به همین دلیل این ماژول فقط پاک‌سازی و بررسی طول را انجام
می‌دهد.

در بلو بانک (شعبهٔ مجازی بانک سامان)، شماره سپرده معمولاً ۱۸ رقم
است. اما در همان متن تراکنش، ممکن است اعداد ۱۸ رقمی دیگری هم
وجود داشته باشد که «شماره سپرده» نیستند (مثلاً «شماره پیگیری» یا
«شماره سند»). به همین دلیل، استخراج با در نظر گرفتن برچسب‌ها
انجام می‌شود:

    - برچسب مثبت: نشانهٔ شماره سپرده
      («شماره سپرده»، «حساب سپرده»، «شماره حساب سپرده»)
    - برچسب منفی: نشانهٔ شماره پیگیری یا سند
      («شماره پیگیری»، «شماره سند»، «کد رهگیری»، ...)

منطق تصمیم‌گیری: برای هر عدد ۱۸ رقمی، نزدیک‌ترین برچسب **قبل از
آن** بررسی می‌شود. اگر نزدیک‌ترین برچسبِ قبل، منفی باشد → عدد رد
می‌شود. اگر مثبت باشد → قبول می‌شود.

این منطق به‌طور طبیعی «گروهی از اعداد زیر یک برچسب» را نیز پشتیبانی
می‌کند: اگر بعد از «شماره پیگیری های» چند عدد ۱۸ رقمی بیاید، همهٔ
آن‌ها رد می‌شوند چون نزدیک‌ترین برچسب قبلی‌شان همان برچسب منفی است.
"""

from __future__ import annotations

import re

from .text import strip_non_digits

__all__ = [
    "DEPOSIT_NUMBER_LENGTH",
    "DEPOSIT_PATTERN",
    "DEPOSIT_LABEL_PATTERN",
    "NEGATIVE_LABEL_PATTERN",
    "POSITIVE_LABEL_PATTERN",
    "clean_deposit_number",
    "is_valid_deposit_number",
    "extract_deposit_number",
]

# طول استاندارد شماره سپرده (برای بلو بانک).
DEPOSIT_NUMBER_LENGTH = 18

# ---------------------------------------------------------------------------
# الگوهای برچسب
# ---------------------------------------------------------------------------

# برچسب‌های مثبت
_POSITIVE_LABELS = (
    r"شماره\s*سپرده"
    r"|حساب\s*سپرده"
    r"|شماره\s*حساب\s*سپرده"
)

# برچسب‌های منفی
_NEGATIVE_LABELS = (
    r"شماره\s*پیگیری"
    r"|کد\s*پیگیری"
    r"|شماره\s*سند"
    r"|کد\s*رهگیری"
    r"|شماره\s*رهگیری"
    r"|شماره\s*ارجاع"
    r"|کد\s*ارجاع"
    r"|شماره\s*مرجع"
    r"|کد\s*مرجع"
    r"|شماره\s*تراکنش"
    r"|کد\s*تراکنش"
)

# ---------------------------------------------------------------------------
# الگوهای عدد و برچسب
# ---------------------------------------------------------------------------

# الگوی عمومی عدد ۱۸ رقمی با جداکنندهٔ اختیاری (فاصله یا خط تیره).
DEPOSIT_PATTERN = re.compile(
    r"(?<!\d)\d(?:[\s\-]?\d){17}(?!\d)"
)

# الگوی برچسب‌دار (برای سازگاری با کدهای قدیمی که از این استفاده
# می‌کردند).
DEPOSIT_LABEL_PATTERN = re.compile(
    rf"(?:{_POSITIVE_LABELS})\s*:?\s*(\d(?:[\s\-]?\d){{15,25}})"
)

# الگو برای پیدا کردن موقعیت برچسب مثبت در متن.
POSITIVE_LABEL_PATTERN = re.compile(rf"(?:{_POSITIVE_LABELS})")

# الگو برای پیدا کردن موقعیت برچسب منفی در متن.
NEGATIVE_LABEL_PATTERN = re.compile(rf"(?:{_NEGATIVE_LABELS})")


# ---------------------------------------------------------------------------
# توابع
# ---------------------------------------------------------------------------

def clean_deposit_number(value: str) -> str:
    """حذف کاراکترهای غیرعددی از یک شماره سپرده."""
    return strip_non_digits(value)


def is_valid_deposit_number(value: str) -> bool:
    """بررسی معتبر بودن یک شماره سپرده بر اساس طول.

    مثال:
        >>> is_valid_deposit_number("123456789012345678")
        True
        >>> is_valid_deposit_number("1234-5678-9012-3456-78")
        True
        >>> is_valid_deposit_number("12345")
        False
    """
    return len(clean_deposit_number(value)) == DEPOSIT_NUMBER_LENGTH


def _nearest_label_end_before(
    label_pattern: re.Pattern, text: str, position: int
) -> int | None:
    """موقعیت پایان نزدیک‌ترین برچسب قبل از `position` را برمی‌گرداند.

    Args:
        label_pattern: الگوی Regex برچسب.
        text: متن کامل.
        position: موقعیت مرجع (مثلاً شروع یک عدد).

    Returns:
        ایندکس پایان نزدیک‌ترین برچسب (کوچک‌تر از position)، یا None
        اگر برچسبی قبل از این موقعیت نباشد.
    """
    best: int | None = None
    for match in label_pattern.finditer(text):
        if match.end() <= position:
            if best is None or match.end() > best:
                best = match.end()
    return best


def _decide_by_context(text: str, number_start: int) -> bool:
    """تصمیم‌گیری بر اساس نزدیک‌ترین برچسبِ قبل از عدد.

    Args:
        text: متن کامل.
        number_start: موقعیت شروع عدد.

    Returns:
        True اگر عدد پذیرفته شود، False اگر رد شود.
    """
    pos_end = _nearest_label_end_before(POSITIVE_LABEL_PATTERN, text, number_start)
    neg_end = _nearest_label_end_before(NEGATIVE_LABEL_PATTERN, text, number_start)

    # هیچ برچسبی قبل نیست: قبول (fallback محافظه‌کارانه)
    if pos_end is None and neg_end is None:
        return True

    # فقط برچسب مثبت: قبول
    if pos_end is not None and neg_end is None:
        return True

    # فقط برچسب منفی: رد
    if pos_end is None and neg_end is not None:
        return False

    # هر دو نزدیک: نزدیک‌تر کدام است؟
    return pos_end > neg_end


def extract_deposit_number(text: str) -> str | None:
    """استخراج شماره سپرده از متن با در نظر گرفتن برچسب‌ها.

    برای هر عدد ۱۸ رقمی در متن، نزدیک‌ترین برچسبِ **قبل از** عدد را
    پیدا می‌کند. اگر آن برچسب منفی باشد، عدد رد می‌شود. اگر مثبت
    باشد، عدد پذیرفته می‌شود.

    این منطق «گروهی از اعداد زیر یک برچسب» را نیز پشتیبانی می‌کند:
    اگر بعد از «شماره پیگیری های» چندین عدد بیاید، همه‌شان رد
    می‌شوند چون نزدیک‌ترین برچسب قبلی‌شان همان برچسب منفی است.

    Args:
        text: متن نرمال‌شده (ارقام ASCII).

    Returns:
        شماره سپردهٔ معتبر یا None.

    مثال:
        >>> extract_deposit_number("شماره سپرده: ۱۲۳۴۵۶۷۸۹۰۱۲۳۴۵۶۷۸")
        '123456789012345678'
        >>> extract_deposit_number("شماره پیگیری: ۱۲۳۴۵۶۷۸۹۰۱۲۳۴۵۶۷۸")
        None
        >>> extract_deposit_number("۱۲۳۴۵۶۷۸۹۰۱۲۳۴۵۶۷۸")
        '123456789012345678'
    """
    for match in DEPOSIT_PATTERN.finditer(text):
        candidate = clean_deposit_number(match.group(0))
        if len(candidate) != DEPOSIT_NUMBER_LENGTH:
            continue

        if _decide_by_context(text, match.start()):
            return candidate

    return None