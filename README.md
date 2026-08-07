# Iranian Bank Transaction Extractor

A command-line tool that extracts and validates card numbers, IBANs (Sheba),
and national IDs from the free-text description field of Iranian bank
transaction exports, identifies the issuing bank for each, and writes a
clean, RTL-formatted Excel report.

Built to solve a real problem: bank transaction exports typically dump all
of this information into a single unstructured description column, mixing
Persian/Arabic digits, inconsistent separators, and invisible Unicode
characters. This tool turns that mess into structured, verifiable data.

## Features

- **Robust text normalization** — handles Persian/Arabic digit variants,
  look-alike Arabic letters, zero-width characters, and inconsistent
  whitespace before any pattern matching happens.
- **Checksum validation, not just pattern matching** — a 16-digit number
  that _looks_ like a card isn't necessarily one (it could be a tracking
  ID). Every candidate is validated with the **Luhn algorithm** (cards) or
  **ISO 7064 MOD 97-10** (IBAN) before being accepted, which meaningfully
  reduces false positives.
- **Bank identification** — resolves the issuing bank from the card BIN
  (first 6 digits) or the IBAN bank code (3-digit segment), against curated
  lookup tables for major Iranian banks.
- **Transaction type filtering** — optionally restrict processing to a
  specific transaction type (e.g. deposits only).
- **RTL-formatted Excel output** — results are written with right-to-left
  sheet orientation and right-aligned cells, ready to open directly in
  Excel.

## Project structure

```text
Iranian-Bank-Transaction-Extractor/
│
├── main.py              # CLI entry point, extraction + validation + Excel output
├── normalize.py          # General-purpose text normalization pipeline
├── constants/
│   ├── card_bins.py       # Card BIN -> bank name lookup table
│   └── iban_banks.py      # IBAN bank code -> bank name lookup table
├── requirements.txt
├── .gitignore
├── LICENSE
└── README.md
```

## Installation

```bash
git clone https://github.com/<your-username>/Iranian-Bank-Transaction-Extractor.git
cd Iranian-Bank-Transaction-Extractor
python3 -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## Usage

```bash
python3 main.py INPUT.xlsx SHEET_NAME DESCRIPTION_COLUMN OUTPUT.xlsx
```

Example:

```bash
python3 main.py transactions.xlsx Sheet1 شرح output.xlsx
```

By default, only rows whose transaction-type column contains the keyword
"واریز" (deposit) are processed. Both the column name and the keyword are
configurable:

```bash
python3 main.py transactions.xlsx Sheet1 شرح output.xlsx \
    --type-column "نوع تراکنش" --deposit-keyword واریز
```

To process every row regardless of transaction type:

```bash
python3 main.py transactions.xlsx Sheet1 شرح output.xlsx --no-filter
```

### Output columns

The output workbook contains all original columns plus:

| Column       | Description                             |
| ------------ | --------------------------------------- |
| `شماره کارت` | Extracted card number (Luhn-valid only) |
| `بانک کارت`  | Card-issuing bank                       |
| `شماره شبا`  | Extracted IBAN (checksum-valid only)    |
| `بانک شبا`   | IBAN-issuing bank                       |
| `کد ملی`     | Extracted national ID                   |

## How it works

```text
raw description text
        ↓
normalize_text()           — Unicode NFKC, digit/letter normalization,
                              zero-width character stripping
        ↓
regex candidate search      — finds ALL card/IBAN-shaped substrings,
                              not just the first
        ↓
checksum validation         — Luhn for cards, MOD 97-10 for IBAN;
                              first valid candidate wins
        ↓
bank lookup                 — BIN / bank-code → bank name
        ↓
Excel report (RTL)
```

## Limitations

The extraction regex patterns are written against the transaction
description format actually observed in this project's data. If your
bank's export uses a meaningfully different format, you may need to adjust
the patterns in `main.py`. National ID extraction is pattern-based only —
it does not currently validate the Iranian national ID checksum (a
different algorithm from Luhn), since the goal here is extraction from
free text rather than identity verification.

## License

MIT — see [LICENSE](LICENSE).

---

## فارسی

ابزاری خط‌فرمانی برای استخراج و اعتبارسنجی شماره کارت، شماره شبا و کد
ملی از ستون شرح تراکنش‌های بانکی، تشخیص بانک صادرکننده، و تولید خروجی
Excel با چیدمان راست‌به‌چپ.

### ویژگی‌ها

- نرمال‌سازی قدرتمند متن (ارقام فارسی/عربی، حروف عربی مشابه، کاراکترهای
  نامرئی، فاصله‌های غیرمعمول) قبل از هرگونه تطبیق الگو
- اعتبارسنجی واقعی به‌جای صرفِ تطبیق الگو: هر عدد کاندید با الگوریتم
  **Luhn** (برای کارت) یا **ISO 7064 MOD 97-10** (برای شبا) بررسی می‌شود
  تا false positive به حداقل برسد
- تشخیص بانک صادرکننده از روی BIN کارت یا کد بانک در شبا
- امکان فیلتر کردن بر اساس نوع تراکنش
- خروجی Excel با جهت راست‌به‌چپ و تراز راست

### نصب و اجرا

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python3 main.py transactions.xlsx Sheet1 شرح output.xlsx
```

### محدودیت‌ها

الگوهای Regex بر اساس فرمت تراکنش‌های مشاهده‌شده در داده‌ی این پروژه
نوشته شده‌اند. اگر فرمت اکسپورت بانک دیگری تفاوت معناداری داشته باشد،
ممکن است لازم باشد الگوها را در `main.py` تنظیم کنی. استخراج کد ملی فقط
بر اساس الگو است و در حال حاضر checksum کد ملی (که الگوریتمی متفاوت از
Luhn دارد) را اعتبارسنجی نمی‌کند، چون هدف این بخش استخراج از متن آزاد
است، نه احراز هویت.
