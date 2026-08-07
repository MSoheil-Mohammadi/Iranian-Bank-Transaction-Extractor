import argparse
import re

import pandas as pd
from openpyxl.styles import Alignment

from normalize import normalize_text
from constants.card_bins import CARD_BANKS
from constants.iban_banks import IBAN_BANKS

CARD_RE = re.compile(r"\b[1-9]\d{3}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b")

IBAN_RE = re.compile(r"IR(?:[\s\-*/]*\d){24}", re.IGNORECASE)

NATIONAL_CODE_RE = re.compile(
    r"IRR[_,،.]*\s*(\d{10})"
    r"|"
    r"(\d{10})\s*[_,،.]*\s*IRR",
    re.IGNORECASE,
)

def clean_card(value: str) -> str:
    """فقط ارقام شماره کارت را نگه می‌دارد."""
    return re.sub(r"\D", "", value)


def clean_iban(value: str) -> str:
    """فاصله‌ها را حذف و حروف را بزرگ می‌کند (IR باید حتماً بزرگ باشد)."""
    return re.sub(r"[^A-Za-z0-9]", "", value).upper()

def luhn_check(card_number: str) -> bool:
    digits = [int(d) for d in card_number[::-1]]
    total = 0
    for i, d in enumerate(digits):
        if i % 2 == 1:
            d *= 2
            if d > 9:
                d -= 9
        total += d
    return total % 10 == 0


def iban_check(iban: str) -> bool:
    if len(iban) != 26 or not iban.startswith("IR"):
        return False

    rearranged = iban[4:] + iban[:4]
    numeric_chars = []
    for ch in rearranged:
        if ch.isdigit():
            numeric_chars.append(ch)
        elif ch.isalpha():
            numeric_chars.append(str(ord(ch.upper()) - ord("A") + 10))
        else:
            return False

    numeric_string = "".join(numeric_chars)
    try:
        return int(numeric_string) % 97 == 1
    except ValueError:
        return False

def get_card_bank(card: str) -> str:
    return CARD_BANKS.get(card[:6], "نامشخص") if len(card) >= 6 else "نامشخص"


def get_iban_bank(iban: str) -> str:
    if not iban.startswith("IR") or len(iban) < 7:
        return "نامشخص"
    bank_code = iban[4:7]
    return IBAN_BANKS.get(bank_code, "نامشخص")

def extract_valid_card(text: str):
    """در متن دنبال همه‌ی الگوهای شبیه کارت می‌گردد و اولین موردی که
    Luhn-valid است را برمی‌گرداند. اگر هیچ‌کدام معتبر نبودند، None."""
    for match in CARD_RE.finditer(text):
        candidate = clean_card(match.group(0))
        if len(candidate) == 16 and luhn_check(candidate):
            return candidate
    return None


def extract_valid_iban(text: str):
    """همان منطق extract_valid_card، اما برای شبا با اعتبارسنجی mod-97."""
    for match in IBAN_RE.finditer(text):
        candidate = clean_iban(match.group(0))
        if iban_check(candidate):
            return candidate
    return None


def extract_national_code(text: str):
    m = NATIONAL_CODE_RE.search(text)
    if m:
        return m.group(1) or m.group(2)
    return None

def process_transactions(
    input_file: str,
    sheet_name: str,
    desc_column: str,
    output_file: str,
    type_column: str = None,
    deposit_keyword: str = None,
) -> None:
    df = pd.read_excel(input_file, sheet_name=sheet_name, dtype=str)

    if desc_column not in df.columns:
        raise ValueError(
            f"ستون شرح '{desc_column}' یافت نشد. ستون‌های موجود: {list(df.columns)}"
        )

    if type_column and deposit_keyword:
        if type_column in df.columns:
            mask = (
                df[type_column]
                .astype(str)
                .str.strip()
                .str.contains(deposit_keyword.strip(), case=False, na=False)
            )
            df = df[mask].copy()
            print(f"تعداد ردیف‌های واریزی: {len(df)}")
        else:
            print(f"هشدار: ستون '{type_column}' یافت نشد. تمام ردیف‌ها پردازش می‌شوند.")
    else:
        print("بدون فیلتر نوع تراکنش – تمام ردیف‌ها پردازش می‌شوند.")

    cards, ibans, national_codes = [], [], []
    card_banks, iban_banks = [], []

    for _, row in df.iterrows():
        text = normalize_text(row[desc_column])

        card = extract_valid_card(text)
        cards.append(card)
        card_banks.append(get_card_bank(card) if card else None)

        iban = extract_valid_iban(text)
        ibans.append(iban)
        iban_banks.append(get_iban_bank(iban) if iban else None)

        national_codes.append(extract_national_code(text))

    df["شماره کارت"] = cards
    df["بانک کارت"] = card_banks
    df["شماره شبا"] = ibans
    df["بانک شبا"] = iban_banks
    df["کد ملی"] = national_codes

    with pd.ExcelWriter(output_file, engine="openpyxl") as writer:
        df.to_excel(writer, sheet_name="Sheet1", index=False)
        ws = writer.sheets["Sheet1"]
        align = Alignment(horizontal="right")
        for row in ws.iter_rows(min_row=1, max_row=ws.max_row, max_col=ws.max_column):
            for cell in row:
                cell.alignment = align
        ws.sheet_view.rightToLeft = True

    print("✅ استخراج با موفقیت انجام شد.")
    print(f"📁 خروجی: {output_file}")
    print(f"🔢 شماره کارت معتبر: {df['شماره کارت'].notna().sum()}")
    print(f"🔢 شبای معتبر: {df['شماره شبا'].notna().sum()}")
    print(f"🔢 کد ملی: {df['کد ملی'].notna().sum()}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="استخراج شماره کارت، شبا و کد ملی از شرح تراکنش‌های بانکی"
    )
    parser.add_argument("input_file")
    parser.add_argument("sheet_name")
    parser.add_argument("desc_column")
    parser.add_argument("output_file")
    parser.add_argument("--type-column", default="نوع")
    parser.add_argument("--deposit-keyword", default="واریز")
    parser.add_argument("--no-filter", action="store_true")

    args = parser.parse_args()
    type_col = None if args.no_filter else args.type_column
    deposit_kw = None if args.no_filter else args.deposit_keyword

    process_transactions(
        args.input_file,
        args.sheet_name,
        args.desc_column,
        args.output_file,
        type_column=type_col,
        deposit_keyword=deposit_kw,
    )