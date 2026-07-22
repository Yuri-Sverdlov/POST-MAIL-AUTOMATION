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

    if len(sys.argv) > 1 and sys.argv[1] == "translate":
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
            elif args[i] == "--account" and i + 1 < len(args):
                os.environ["IMAP_USER"] = args[i + 1]
                i += 2
            else:
                print(f"Unknown argument: {args[i]}")
                print("Usage: python -m app export [--days N] [--limit N] [--output file.txt] [--from FILTER] [--account EMAIL]")
                sys.exit(1)
        export_emails(days=days, limit=limit, output=output, from_filter=from_filter)

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
        print("  python -m app export [--days N] [--limit N] [--output file.txt] [--from FILTER] [--account EMAIL]")
        print("  python -m app aliexpress [--days N] [--limit N] [--account EMAIL]")