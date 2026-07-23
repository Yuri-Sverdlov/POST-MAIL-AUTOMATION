import sys
import os
from app.imap_client import list_inbox, fetch_message, export_emails
from app.translator import translate_subject, translate_body

if __name__ == "__main__":
    # Global --account override (before command dispatch)
    args_list = sys.argv[1:]
    for ai, arg in enumerate(args_list):
        if arg == "--account" and ai + 1 < len(args_list):
            os.environ["IMAP_USER"] = args_list[ai + 1]
            sys.argv = [sys.argv[0]] + args_list[:ai] + args_list[ai+2:]
            break

    if len(sys.argv) > 1 and sys.argv[1] in ("help", "--help", "-h"):
        print("POST-MAIL-AUTOMATION\n")
        print("Commands:")
        print("  python -m app                                    Show 5 recent inbox messages")
        print("  python -m app translate <UID>                    Translate email to Russian")
        print("  python -m app export [options]                   Export emails to text file")
        print("  python -m app aliexpress [options]               Track AliExpress orders")
        print("\nOptions for export:")
        print("  --days N          Last N days (default 7)")
        print("  --limit N         Max emails (default 20)")
        print("  --from ADDR       Filter by sender")
        print("  --output FILE     Output filename (default exported_emails.txt)")
        print("  --translate       Auto-translate bodies to Russian")
        print("  --from-date YYYY-MM-DD   Start date (inclusive)")
        print("  --to-date YYYY-MM-DD     End date (inclusive)")
        print("  --before YYYY-MM-DD      Emails strictly before date")
        print("  --after YYYY-MM-DD       Emails strictly after date")
        print("  --skip-newsletters       Filter out newsletter/spam emails")
        print("  --account EMAIL   Switch Gmail account")
        print("\nOptions for aliexpress:")
        print("  --days N        Last N days (default 365)")
        print("  --limit N       Max emails (default 200)")
        print("  --account EMAIL Switch Gmail account")
        sys.exit(0)

    elif len(sys.argv) > 1 and sys.argv[1] == "translate":
        uid = sys.argv[2] if len(sys.argv) > 2 else None
        if uid:
            msg = fetch_message(uid)
            if msg:
                print(f"Original: {msg['subject']}")
                print(f"Translation: {translate_subject(msg['subject'])}")
                print(f"\n--- Body ---")
                print(f"Original ({len(msg['body'])} chars):")
                print(msg['body'][:500])
                print(f"\n--- Translation ---")
                print(translate_body(msg['body']))
            else:
                print(f"Message {uid} not found")
        else:
            print("Usage: python -m app translate <uid>")

    elif len(sys.argv) > 1 and sys.argv[1] == "export":
        days = 7
        limit = 20
        output = "exported_emails.txt"
        from_filter = None
        translate = False
        from_date = None
        to_date = None
        before = None
        after = None
        skip_newsletters = False
        args = sys.argv[2:]
        i = 0
        while i < len(args):
            if args[i] == "--days" and i + 1 < len(args):
                days = int(args[i + 1])
                i += 2
            elif args[i] == "--limit" and i + 1 < len(args):
                limit = int(args[i + 1])
                i += 2
            elif args[i] == "--output" and i + 1 < len(args):
                output = args[i + 1]
                i += 2
            elif args[i] == "--from" and i + 1 < len(args):
                from_filter = args[i + 1]
                i += 2
            elif args[i] == "--translate":
                translate = True
                i += 1
            elif args[i] == "--from-date" and i + 1 < len(args):
                from_date = args[i + 1]
                i += 2
            elif args[i] == "--to-date" and i + 1 < len(args):
                to_date = args[i + 1]
                i += 2
            elif args[i] == "--before" and i + 1 < len(args):
                before = args[i + 1]
                i += 2
            elif args[i] == "--after" and i + 1 < len(args):
                after = args[i + 1]
                i += 2
            elif args[i] == "--skip-newsletters":
                skip_newsletters = True
                i += 1
            elif args[i] == "--account" and i + 1 < len(args):
                os.environ["IMAP_USER"] = args[i + 1]
                i += 2
            else:
                print(f"Unknown argument: {args[i]}")
                print("Usage: python -m app export [--days N] [--limit N] [--output file.txt] [--from ADDR] [--translate] [--from-date DATE] [--to-date DATE] [--before DATE] [--after DATE] [--skip-newsletters] [--account EMAIL]")
                sys.exit(1)
        export_emails(days=days, limit=limit, output=output, from_filter=from_filter,
                      translate=translate, from_date=from_date, to_date=to_date,
                      before=before, after=after, skip_newsletters=skip_newsletters)

    elif len(sys.argv) > 1 and sys.argv[1] == "aliexpress":
        from app.aliexpress import fetch_aliexpress_emails, save_txt_report, save_xlsx_report
        days = 365
        limit = 200
        args = sys.argv[2:]
        i = 0
        while i < len(args):
            if args[i] == "--days" and i + 1 < len(args):
                days = int(args[i + 1]); i += 2
            elif args[i] == "--limit" and i + 1 < len(args):
                limit = int(args[i + 1]); i += 2
            else:
                print(f"Unknown: {args[i]}"); sys.exit(1)
        orders = fetch_aliexpress_emails(days=days, limit=limit)
        save_txt_report(orders, "aliexpress_orders.txt")
        save_xlsx_report(orders, "aliexpress_orders.xlsx")
        transactions = [o for o in orders if o["type"] == "transaction"]
        promos = [o for o in orders if o["type"] == "promo"]
        print(f"\nSummary: {len(transactions)} transactional, {len(promos)} promotional")

    else:
        list_inbox()
        print("\nCommands:")
        print("  python -m app translate <uid>")
        print("  python -m app export [--days N] [--limit N] [--output file.txt] [--from ADDR] [--translate] [--from-date DATE] [--to-date DATE] [--before DATE] [--after DATE] [--skip-newsletters] [--account EMAIL]")
        print("  python -m app aliexpress [--days N] [--limit N] [--account EMAIL]")