"""
پاک‌سازی فاصله‌ها و کاراکترهای نامرئی.

متن‌های کپی‌شده از وب، PDF یا سیستم‌های بانکی ممکن است شامل
کاراکترهای نامرئی یا فاصله‌های غیرمعمول باشند که تطبیق Regex را
خراب می‌کنند. این ماژول همهٔ آن‌ها را پاک‌سازی می‌کند.
"""

from __future__ import annotations

import re

__all__ = ["normalize_whitespace"]

# کاراکترهای عرض‌صفر (Zero-Width) که در متن دیده نمی‌شوند ولی وجود دارند.
# مهم‌ترینشان نیم‌فاصله (ZWNJ) است که در فارسی بسیار رایج است.
_ZERO_WIDTH_CHARS = (
    "\u200b"  # Zero-Width Space
    "\u200c"  # ZWNJ (نیم‌فاصله)
    "\u200d"  # ZWJ (Zero-Width Joiner)
    "\u200e"  # Left-to-Right Mark
    "\u200f"  # Right-to-Left Mark
    "\ufeff"  # Zero-Width No-Break Space (BOM)
)
_ZERO_WIDTH_RE = re.compile(f"[{_ZERO_WIDTH_CHARS}]")

# فاصله‌های غیرمعمول یونیکد که باید به فاصلهٔ معمولی تبدیل شوند.
_EXOTIC_SPACES_RE = re.compile(
    "["
    "\u00a0"          # No-Break Space
    "\u2000-\u200a"   # En/Em و دیگر فاصله‌های یونیکد
    "\u202f"          # Narrow No-Break Space
    "\u205f"          # Medium Mathematical Space
    "\u3000"          # Ideographic Space (فاصلهٔ چینی/ژاپنی)
    "]"
)


def normalize_whitespace(text: str) -> str:
    """پاک‌سازی و یکسان‌سازی فاصله‌ها و کاراکترهای نامرئی.

    عملیات انجام‌شده به ترتیب:

        ۱. حذف کاراکترهای عرض‌صفر (نیم‌فاصله، ZWJ، ZWSP و ...).
        ۲. تبدیل فاصله‌های عجیب یونیکد به فاصلهٔ معمولی.
        ۳. تبدیل چند فاصله یا تب متوالی به یک فاصله.
        ۴. حذف فاصله‌های ابتدا و انتهای رشته.

    Args:
        text: متن ورودی.

    Returns:
        متن نرمال‌شده.

    مثال:
        >>> normalize_whitespace("سلام\u200cجهان")
        'سلامجهان'
        >>> normalize_whitespace("  a    b  ")
        'a b'
        >>> normalize_whitespace("a\\u00a0b")
        'a b'
    """
    text = _ZERO_WIDTH_RE.sub("", text)
    text = _EXOTIC_SPACES_RE.sub(" ", text)
    text = re.sub(r"[ \t]+", " ", text)
    return text.strip()