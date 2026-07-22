---
name: mail-aliexpress
description: Use when the user wants to track AliExpress orders. Parses transactional emails, filters out promotions, outputs chronological txt report and Excel table.
version: 1.0.0
author: POST-MAIL-AUTOMATION project
platforms: [windows]
metadata:
  hermes:
    tags: [mail, aliexpress, orders, tracking, excel]
    category: mail
---

# Mail AliExpress Tracker

Track AliExpress orders from Gmail.

## When to Use

- User asks about AliExpress orders, tracking, delivery status.
- User says "show my AliExpress orders" or "check where my packages are".

## Procedure

1. Change to the project root directory (where `app/` lives).
2. Run from the project root:

```
python -m app aliexpress --account sverdlovy@gmail.com --days 90 --limit 100
```

Note: `--account` must be the Gmail that receives AliExpress emails.

## Output Files

- `aliexpress_orders.txt` — chronological text report.
- `aliexpress_orders.xlsx` — Excel table with columns: Date, Order ID, Tracking ID, Status, Subject.

## Pitfalls

- Only transactional emails from `transaction@notice.aliexpress.com` are included.
- Promotional emails (promo, discounts, recommendations) are automatically filtered out.
- Requires `openpyxl` installed (`pip install openpyxl`).

## Verification

- Both output files are created in the project root.
- Summary line shows number of transactional vs promotional emails.
- Excel file opens with correct column headers.
