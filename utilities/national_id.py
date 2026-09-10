"""
اعتبارسنجی کد ملی ایران.

کد ملی ایران یک عدد ۱۰ رقمی است که رقم دهم آن با یک الگوریتم چک‌سام
مشخص (متفاوت از Luhn و Mod 97) محاسبه می‌شود. این ماژول الگوهای
استخراج، پاک‌سازی و اعتبارسنجی کد ملی را فراهم می‌کند.

الگوریتم چک‌سام:

    فرض کن ارقام کد ملی: d1 d2 d3 d4 d5 d6 d7 d8 d9 d10
    (d10 رقم کنترلی است.)

    ۱. مجموع وزنی: s = d1×10 + d2×9 + ... + d9×2
    ۲. باقی‌مانده: r = s % 11
    ۳. رقم کنترلی مورد انتظار:
           اگر r < 2: expected = r
           وگرنه:     expected = 11 - r
    ۴. اگر expected == d10 → معتبر

نکته:
    کدهایی با ارقام یکسان (مثل 1111111111) از نظر الگوریتم معتبر
    محسوب می‌شوند ولی در عمل کد ملی نیستند؛ این ماژول آن‌ها را رد
    می‌کند.

نکته:
    چک‌سام یک اعتبارسنجی ساختاری است، نه احراز هویت.
"""

from __future__ import annotations

import re

from utilities.text import strip_non_digits

__all__ = [
    "NATIONAL_CODE_LENGTH",
    "NATIONAL_CODE_PATTERN",
    "IRR_NATIONAL_CODE_PATTERN",
    "clean_national_code",
    "national_code_check",
    "is_valid_national_code",
]

# طول یک کد ملی معتبر.
NATIONAL_CODE_LENGTH = 10

# الگوی عمومی کد ملی: دقیقاً ۱۰ رقم پیوسته.
# برای استخراج از متن‌های آزاد که کد ملی بدون زمینه می‌آید کاربرد دارد.
NATIONAL_CODE_PATTERN = re.compile(r"\b\d{10}\b")

# الگوی کد ملی همراه با IRR.
# در تراکنش‌های بانکی، کد ملی معمولاً با پیشوند یا پسوند «IRR» می‌آید:
#     - «IRR 1234567890»
#     - «1234567890 IRR»
IRR_NATIONAL_CODE_PATTERN = re.compile(
    r"IRR[_,،.]*\s*(\d{10})"
    r"|"
    r"(\d{10})\s*[_,،.]*\s*IRR",
    re.IGNORECASE,
)


def clean_national_code(value: str) -> str:
    """حذف کاراکترهای غیرعددی از یک کد ملی.

    این تابع یک alias برای `utilities.text.strip_non_digits` است و
    صرفاً برای خوانایی بیشتر در context کد ملی وجود دارد.

    این تابع **اعتبارسنجی انجام نمی‌دهد**. اعتبارسنجی واقعی باید با
    `national_code_check` یا `is_valid_national_code` انجام شود.

    Args:
        value: رشتهٔ خام کد ملی.

    Returns:
        رشته‌ای که فقط شامل ارقام است.
    """
    return strip_non_digits(value)


def national_code_check(code: str) -> bool:
    """اعتبارسنجی یک کد ملی ۱۰ رقمی با الگوریتم چک‌سام.

    Args:
        code: رشته‌ای از ۱۰ رقم (بدون جداکننده).

    Returns:
        اگر کد ملی معتبر باشد True، در غیر این صورت False.

    مثال:
        >>> national_code_check("0499370899")
        True
        >>> national_code_check("1111111111")
        False
        >>> national_code_check("1234567890")
        False
        >>> national_code_check("")
        False
    """
    # محافظ: طول و نوع کاراکترها
    if not code or len(code) != NATIONAL_CODE_LENGTH or not code.isdigit():
        return False

    # رد کردن کدهای با ارقام یکسان (مثل 1111111111)
    if code == code[0] * NATIONAL_CODE_LENGTH:
        return False

    # محاسبهٔ مجموع وزنی ۹ رقم اول
    total = sum(int(code[i]) * (10 - i) for i in range(9))

    # محاسبهٔ رقم کنترلی مورد انتظار
    remainder = total % 11
    expected_check_digit = remainder if remainder < 2 else 11 - remainder

    return expected_check_digit == int(code[9])


def is_valid_national_code(code: str) -> bool:
    """بررسی معتبر بودن یک کد ملی خام به‌صورت یک‌جا.

    ترکیبی از پاک‌سازی و اعتبارسنجی چک‌سام.

    Args:
        code: رشتهٔ خام کد ملی.

    Returns:
        اگر کد ملی پس از پاک‌سازی معتبر باشد True، در غیر این صورت False.
    """
    return national_code_check(clean_national_code(code))