import re
import unicodedata

_PERSIAN_DIGITS = "۰۱۲۳۴۵۶۷۸۹"
_ARABIC_DIGITS = "٠١٢٣٤٥٦٧٨٩"
_ASCII_DIGITS = "0123456789"

_DIGIT_TRANSLATION = str.maketrans(
    _PERSIAN_DIGITS + _ARABIC_DIGITS,
    _ASCII_DIGITS + _ASCII_DIGITS,
)


def normalize_digits(text: str) -> str:
    return text.translate(_DIGIT_TRANSLATION)


_ARABIC_TO_PERSIAN_LETTERS = {
    "ي": "ی",
    "ى": "ی",
    "ك": "ک",
}
_LETTER_TRANSLATION = str.maketrans(_ARABIC_TO_PERSIAN_LETTERS)


def normalize_letters(text: str) -> str:
    return text.translate(_LETTER_TRANSLATION)


_ZERO_WIDTH_CHARS = (
    "\u200b"
    "\u200c"
    "\u200d"
    "\u200e"
    "\u200f"
    "\ufeff"
)
_ZERO_WIDTH_RE = re.compile(f"[{_ZERO_WIDTH_CHARS}]")

_EXOTIC_SPACES_RE = re.compile(
    "["
    "\u00a0"
    "\u2000-\u200a"
    "\u202f"
    "\u205f"
    "\u3000"
    "]"
)


def normalize_whitespace(text: str) -> str:
    text = _ZERO_WIDTH_RE.sub("", text)
    text = _EXOTIC_SPACES_RE.sub(" ", text)
    text = re.sub(r"[ \t]+", " ", text)
    return text.strip()


_PUNCTUATION_TRANSLATION = str.maketrans({
    "،": ",",
    "؛": ";",
    "؟": "?",
    "ـ": "",
})


def normalize_punctuation(text: str) -> str:
    return text.translate(_PUNCTUATION_TRANSLATION)


def normalize_text(value) -> str:
    if value is None:
        return ""
    try:
        if value != value:
            return ""
    except Exception:
        pass

    text = str(value)
    text = unicodedata.normalize("NFKC", text)
    text = normalize_digits(text)
    text = normalize_letters(text)
    text = normalize_whitespace(text)
    text = normalize_punctuation(text)
    return text


if __name__ == "__main__":
    samples = [
        "کارت: ۶۰۳۷-۹۹۱۲-۳۴۵۶-۷۸۹۰",
        "شبا:‌ IR12 3456 7890 1234 5678 9012 34",
        "كارت‌ من  ي  دارم",
        "مبلغ:\u00a01,234,567 ریال؛ بابت واریز",
    ]
    for s in samples:
        print(repr(s), "->", repr(normalize_text(s)))