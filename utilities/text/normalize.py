"""
تابع جامع نرمال‌سازی متن.

این ماژول تابع اصلی `normalize_text` را ارائه می‌دهد که همهٔ مراحل
نرمال‌سازی (ارقام، حروف، فاصله‌ها، علائم نگارشی) را به ترتیب صحیح
ترکیب می‌کند. این تابع همان چیزی است که معمولاً در پروژه‌ها
مستقیم استفاده می‌شود.
"""

from __future__ import annotations

import unicodedata

from .digits import normalize_digits
from .letters import normalize_letters
from .punctuation import normalize_punctuation
from .whitespace import normalize_whitespace

__all__ = ["normalize_text"]


def normalize_text(value) -> str:
    """نرمال‌سازی کامل یک متن با اعمال همهٔ مراحل پاک‌سازی.

    مراحل به ترتیب:

        ۱. مدیریت مقادیر خالی (None، NaN).
        ۲. نرمال‌سازی یونیکد با NFKC.
        ۳. تبدیل ارقام فارسی/عربی به ASCII.
        ۴. یکسان‌سازی حروف عربی (ي، ى، ك).
        ۵. پاک‌سازی فاصله‌ها و کاراکترهای نامرئی.
        ۶. یکسان‌سازی علائم نگارشی.

    Args:
        value: مقدار ورودی که ممکن است None، NaN یا هر شیء دیگری باشد.

    Returns:
        رشتهٔ نرمال‌شده. اگر ورودی None یا NaN باشد، رشتهٔ خالی برمی‌گرداند.

    مثال:
        >>> normalize_text("کارت: ۶۰۳۷-۹۹۱۲-۳۴۵۶-۷۸۹۰")
        'کارت: 6037-9912-3456-7890'
        >>> normalize_text("كارت‌ من  ي  دارم")
        'کارت من ی دارم'
        >>> normalize_text(None)
        ''
    """
    # مدیریت مقادیر خالی (None و NaN)
    if value is None:
        return ""

    # چک NaN بدون نیاز به numpy
    # در پایتون، هر NaN با خودش برابر نیست.
    try:
        if value != value:
            return ""
    except Exception:
        pass

    text = str(value)

    # گام ۱: نرمال‌سازی یونیکد (تبدیل کاراکترهای ترکیبی به شکل استاندارد)
    text = unicodedata.normalize("NFKC", text)

    # گام ۲ تا ۵: اعمال نرمال‌سازی‌های تخصصی
    text = normalize_digits(text)
    text = normalize_letters(text)
    text = normalize_whitespace(text)
    text = normalize_punctuation(text)

    return text
