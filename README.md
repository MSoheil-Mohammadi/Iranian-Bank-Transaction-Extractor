# Iranian Bank Transaction Extractor

A command-line tool that extracts and validates card numbers, IBANs
(Sheba), and national IDs from the free-text description field of
Iranian bank transaction exports, identifies the issuing bank for each,
and writes a clean, RTL-formatted Excel or CSV report.

Built to solve a real problem: bank transaction exports typically dump
all of this information into a single unstructured description column,
mixing Persian/Arabic digits, inconsistent separators, and invisible
Unicode characters. This tool turns that mess into structured,
verifiable data.

## Features

- **Robust text normalization** — handles Persian/Arabic digit
  variants, look-alike Arabic letters, zero-width characters, and
  inconsistent whitespace before any pattern matching happens.
- **Checksum validation, not just pattern matching** — a 16-digit
  number that looks like a card isn't necessarily one (it could be a
  tracking ID). Every candidate is validated with the **Luhn algorithm**
  (cards), **ISO 7064 MOD 97-10** (IBAN), or the **Iranian national ID
  checksum** before being accepted, which meaningfully reduces false
  positives.
- **Bank identification** — resolves the issuing bank from the card BIN
  (first 6 digits) or the IBAN bank code (3-digit segment), against
  curated lookup tables for major Iranian banks.
- **Transaction type filtering** — optionally restrict processing to a
  specific transaction type (e.g. deposits only).
- **CSV and Excel support** — reads and writes both `.xlsx` and `.csv`.
  The output format is chosen automatically from the output file
  extension.
- **Large-file friendly** — uses vectorized pandas operations and skips
  heavy Excel styling when the row count exceeds a configurable
  threshold.
- **RTL-formatted Excel output** — results are written with right-to-left
  sheet orientation and right-aligned cells, ready to open directly in
  Excel.

## Project structure

```text
Iranian-Bank-Transaction-Extractor/
│
├── main.py                    # CLI entry point
├── utilities/                 # Reusable validation & normalization helpers
│   ├── luhn.py                #   Luhn (Mod 10) for card numbers
│   ├── iban.py                #   Mod 97 (ISO 13616) for Sheba
│   ├── national_id.py         #   Iranian national ID checksum
│   ├── text/                  #   Persian/Arabic text normalization
│   │   ├── digits.py
│   │   ├── letters.py
│   │   ├── whitespace.py
│   │   ├── punctuation.py
│   │   └── normalize.py
│   └── README.md
├── constants/                 # Static lookup tables
│   ├── card_bins.py           #   Card BIN -> bank name
│   └── iban_banks.py          #   IBAN bank code -> bank name
├── requirements.txt
├── .gitignore
├── LICENSE
└── README.md
```

## Installation

```bash
git clone https://github.com/MSoheil-Mohammadi/Iranian-Bank-Transaction-Extractor.git
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

By default, only rows whose transaction-type column contains the
keyword "واریز" (deposit) are processed. Both the column name and the
keyword are configurable:

```bash
python3 main.py transactions.xlsx Sheet1 شرح output.xlsx \
    --type-column "نوع تراکنش" --deposit-keyword واریز
```

To process every row regardless of transaction type:

```bash
python3 main.py transactions.xlsx Sheet1 شرح output.xlsx --no-filter
```

To write the output as CSV instead of Excel, just change the extension:

```bash
python3 main.py transactions.xlsx Sheet1 شرح output.csv
```

### Output columns

The output contains all original columns plus:

| Column       | Description                                 |
| ------------ | ------------------------------------------- |
| `شماره کارت` | Extracted card number (Luhn-valid only)     |
| `بانک کارت`  | Card-issuing bank                           |
| `شماره شبا`  | Extracted IBAN (Mod 97-valid only)          |
| `بانک شبا`   | IBAN-issuing bank                           |
| `کد ملی`     | Extracted national ID (checksum-valid only) |

## How it works

```text
raw description text
        ↓
normalize_text()            — Unicode NFKC, digit/letter normalization,
                              zero-width character stripping
        ↓
regex candidate search      — finds ALL card/IBAN-shaped substrings,
                              not just the first
        ↓
checksum validation         — Luhn for cards, Mod 97 for IBAN,
                              national ID checksum for codes;
                              first valid candidate wins
        ↓
bank lookup                 — BIN / bank-code → bank name
        ↓
Excel or CSV output (RTL)
```

## Performance notes

- Uses `pandas.Series.progress_apply` instead of `DataFrame.iterrows()`,
  which is significantly faster for large files.
- Excel styling (table, cell alignment, freeze panes) is skipped when
  the number of rows exceeds `STYLE_THRESHOLD` (50,000 by default,
  defined in `main.py`). This keeps write time reasonable for very
  large files.
- For maximum performance with huge datasets, prefer CSV output over
  Excel.

## Limitations

The extraction regex patterns are written against the transaction
description format actually observed in this project's data. If your
bank's export uses a meaningfully different format, you may need to
adjust the patterns in `main.py`.

## License

MIT — see [LICENSE](LICENSE).

---

## فارسی

ابزاری خط‌فرمانی برای استخراج و اعتبارسنجی شماره کارت، شماره شبا و
کد ملی از ستون شرح تراکنش‌های بانکی، تشخیص بانک صادرکننده، و تولید
خروجی Excel یا CSV با چیدمان راست‌به‌چپ.

### ویژگی‌ها

- نرمال‌سازی قدرتمند متن (ارقام فارسی/عربی، حروف عربی مشابه،
  کاراکترهای نامرئی، فاصله‌های غیرمعمول) قبل از هرگونه تطبیق الگو
- اعتبارسنجی واقعی به‌جای صرفِ تطبیق الگو: هر عدد کاندید با الگوریتم
  **Luhn** (برای کارت)، **ISO 7064 MOD 97-10** (برای شبا)، یا
  **چک‌سام کد ملی ایران** (برای کد ملی) بررسی می‌شود تا false
  positive به حداقل برسد
- تشخیص بانک صادرکننده از روی BIN کارت یا کد بانک در شبا
- امکان فیلتر کردن بر اساس نوع تراکنش
- پشتیبانی از ورودی و خروجی CSV و Excel (فرمت بر اساس پسوند فایل
  انتخاب می‌شود)
- بهینه برای فایل‌های بزرگ (استایل‌دهی اکسل در فایل‌های بزرگ‌تر از
  حد آستانه غیرفعال می‌شود)
- خروجی Excel با جهت راست‌به‌چپ و تراز راست

### ساختار پروژه

```text
Iranian-Bank-Transaction-Extractor/
│
├── main.py                    # نقطهٔ ورود خط فرمان
├── utilities/                 # ابزارهای اعتبارسنجی و نرمال‌سازی
│   ├── luhn.py                #   الگوریتم Luhn برای کارت بانکی
│   ├── iban.py                #   الگوریتم Mod 97 برای شبا
│   ├── national_id.py         #   چک‌سام کد ملی ایران
│   ├── text/                  #   نرمال‌سازی متن فارسی/عربی
│   └── README.md
├── constants/                 # جدول‌های دادهٔ ثابت
│   ├── card_bins.py           #   BIN کارت به نام بانک
│   └── iban_banks.py          #   کد بانک شبا به نام بانک
├── requirements.txt
├── .gitignore
├── LICENSE
└── README.md
```

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
ممکن است لازم باشد الگوها را در `main.py` تنظیم کنی.
