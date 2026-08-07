import argparse
import re

import pandas as pd
from openpyxl.styles import Alignment, numbers
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.table import Table, TableStyleInfo
from tqdm import tqdm

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

def clean_card(val: str) -> str:
    return re.sub(r"\D", "", val)


def clean_iban(val: str) -> str:
    return re.sub(r"[^A-Za-z0-9]", "", val).upper()

def luhn_check(card: str) -> bool:
    digits = [int(d) for d in card[::-1]]
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
    num_str = ""
    for ch in rearranged:
        if ch.isdigit():
            num_str += ch
        elif ch.isalpha():
            num_str += str(ord(ch.upper()) - 55)
        else:
            return False
    return int(num_str) % 97 == 1


def get_card_bank(card: str) -> str:
    return CARD_BANKS.get(card[:6], "نامشخص") if len(card) >= 6 else "نامشخص"


def get_iban_bank(iban: str) -> str:
    if iban.startswith("IR") and len(iban) >= 7:
        return IBAN_BANKS.get(iban[4:7], "نامشخص")
    return "نامشخص"


def extract_valid_card(text: str):
    for match in CARD_RE.finditer(text):
        c = clean_card(match.group(0))
        if len(c) == 16 and luhn_check(c):
            return c
    return None


def extract_valid_iban(text: str):
    for match in IBAN_RE.finditer(text):
        c = clean_iban(match.group(0))
        if iban_check(c):
            return c
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
        raise ValueError(f"ستون '{desc_column}' یافت نشد.")

    if type_column and deposit_keyword:
        if type_column in df.columns:
            mask = df[type_column].str.strip().str.contains(
                deposit_keyword.strip(), case=False, na=False
            )
            df = df[mask].copy()
            print(f"تعداد ردیف‌های واریزی: {len(df)}")
        else:
            print(f"هشدار: ستون '{type_column}' یافت نشد. تمام ردیف‌ها پردازش می‌شوند.")

    cards, card_banks = [], []
    ibans, iban_banks = [], []
    national_codes = []

    tqdm.pandas(desc="در حال پردازش ردیف‌ها")
    for _, row in tqdm(df.iterrows(), total=len(df)):
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

        align = Alignment(horizontal="right", vertical="center")
        ws.sheet_view.rightToLeft = True

        for col_idx, col_name in enumerate(df.columns, 1):
            width = max(len(str(col_name)) * 1.3, 12)
            ws.column_dimensions[get_column_letter(col_idx)].width = min(width, 35)

        last_row = len(df) + 1
        last_col = get_column_letter(len(df.columns))
        table_ref = f"A1:{last_col}{last_row}"
        tab = Table(displayName="Transactions", ref=table_ref)

        style = TableStyleInfo(
            name="TableStyleMedium2",
            showFirstColumn=False,
            showLastColumn=False,
            showRowStripes=True,
            showColumnStripes=False,
        )
        tab.tableStyleInfo = style
        ws.add_table(tab)

        for row in ws.iter_rows(min_row=2, max_row=last_row, max_col=len(df.columns)):
            for cell in row:
                cell.alignment = align

        ws.freeze_panes = "A2"

    print("✅ استخراج با موفقیت انجام شد.")
    print(f"📁 خروجی: {output_file}")
    print(f"🔢 کارت‌های معتبر: {df['شماره کارت'].notna().sum()}")
    print(f"🔢 شباهای معتبر: {df['شماره شبا'].notna().sum()}")
    print(f"🔢 کدهای ملی: {df['کد ملی'].notna().sum()}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="استخراج سریع اطلاعات بانکی از فایل اکسل")
    parser.add_argument("input_file", help="فایل اکسل ورودی")
    parser.add_argument("sheet_name", help="نام شیت")
    parser.add_argument("desc_column", help="ستون شرح تراکنش")
    parser.add_argument("output_file", help="فایل خروجی")
    parser.add_argument(
        "--type-column",
        default=None,
        help="ستون نوع تراکنش (مثلاً 'نوع') – برای فیلتر واریز الزامی است",
    )
    parser.add_argument("--deposit-keyword", default="واریز", help="کلیدواژه واریز")
    parser.add_argument("--no-filter", action="store_true", help="نادیده گرفتن فیلتر واریز")

    args = parser.parse_args()

    if args.no_filter:
        type_col = None
        deposit_kw = None
    else:
        type_col = args.type_column
        deposit_kw = args.deposit_keyword if type_col else None

    process_transactions(
        args.input_file,
        args.sheet_name,
        args.desc_column,
        args.output_file,
        type_column=type_col,
        deposit_keyword=deposit_kw,
    )