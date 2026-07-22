import re
from datetime import datetime, timedelta, timezone
from imap_tools import MailBox, A

ORDER_RE = re.compile(r"(?:Заказ(?:ать)?|Order)\s+(\d{16})", re.IGNORECASE)
TRACKING_RE = re.compile(r"Package\s+(AE\d+)", re.IGNORECASE)
TRACELOG_EVENT_RE = re.compile(r"tracelog=[^&]*?-(\d+)-([a-z_]+)_")

STATUS_MAP = {
    "buyer_accept_goods_timeout": "Ожидает подтверждения",
    "waiting_to_leave_feedback":  "Доставлен (ожидает отзыва)",
    "extend_confirm_order":       "Подтверждение продлено",
    "lg_del_done_door":           "Доставлен до двери",
    "shipped":                    "Отправлен",
    "arrived_at_customs":         "Прибыл на таможню",
}

SENDER_TRANSACTIONAL = "transaction@notice.aliexpress.com"
ALIEXPRESS_DOMAINS = ("aliexpress.com", "aliexpress.ru", "aliexpress.co.il")


def _connect():
    from app.oauth_auth import get_access_token
    from app.config import IMAP_HOST, get_imap_user
    user = get_imap_user()
    token = get_access_token(user)
    return MailBox(IMAP_HOST).xoauth2(user, token)


def _is_aliexpress(from_addr: str) -> bool:
    return any(d in from_addr.lower() for d in ALIEXPRESS_DOMAINS)


def _classify_email(msg) -> dict | None:
    if not _is_aliexpress(msg.from_):
        return None
    from_lower = msg.from_.lower()
    is_transactional = SENDER_TRANSACTIONAL in from_lower

    if not is_transactional:
        return {"type": "promo", "subject": msg.subject, "date": msg.date}

    order_id = None
    tracking_id = None
    m = ORDER_RE.search(msg.subject)
    if m:
        order_id = m.group(1)
    m = TRACKING_RE.search(msg.subject)
    if m:
        tracking_id = m.group(1)

    status_raw = "unknown"
    body = msg.text or msg.html or ""
    em = TRACELOG_EVENT_RE.search(body)
    if em:
        event_key = em.group(2)
        status_raw = STATUS_MAP.get(event_key, event_key)

    if "ожидает подтверждения" in msg.subject.lower() or "buyer_accept_goods" in body:
        status_raw = "Ожидает подтверждения"
    elif "как все прошло" in msg.subject.lower() or "waiting_to_leave_feedback" in body:
        status_raw = "Доставлен (ожидает отзыва)"
    elif "продлено" in msg.subject.lower() or "extend_confirm" in body:
        status_raw = "Подтверждение продлено"
    elif "delivered" in msg.subject.lower() or "lg_del_done" in body:
        status_raw = "Доставлен до двери"

    return {
        "type": "transaction",
        "order_id": order_id,
        "tracking_id": tracking_id,
        "status": status_raw,
        "subject": msg.subject,
        "date": msg.date,
        "uid": msg.uid,
    }


def fetch_aliexpress_emails(days: int = 90, limit: int = 100):
    since = (datetime.now(timezone.utc) - timedelta(days=days)).date()
    with _connect() as mailbox:
        raw_msgs = list(mailbox.fetch(A(date_gte=since), limit=limit, reverse=True))
        results = []
        for msg in raw_msgs:
            parsed = _classify_email(msg)
            if parsed:
                results.append(parsed)
        return results


def save_txt_report(orders: list, output: str = "aliexpress_orders.txt"):
    with open(output, "w", encoding="utf-8") as f:
        f.write("ALIEXPRESS ORDERS — CHRONOLOGICAL REPORT\n")
        f.write("=" * 70 + "\n\n")
        for item in orders:
            if item["type"] == "promo":
                continue
            oid = item.get("order_id") or item.get("tracking_id") or "N/A"
            dt = item["date"]
            f.write(f"[{dt.strftime('%Y-%m-%d %H:%M')}] Order: {oid}\n")
            f.write(f"  Status:  {item['status']}\n")
            f.write(f"  Subject: {item['subject']}\n")
            f.write("-" * 50 + "\n")
        total = sum(1 for i in orders if i["type"] == "transaction")
        f.write(f"\nTotal: {total} orders\n")
    print(f"Saved {total} orders to {output}")


def save_xlsx_report(orders: list, output: str = "aliexpress_orders.xlsx"):
    try:
        import openpyxl
    except ImportError:
        print("openpyxl not installed. Run: pip install openpyxl")
        return
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "AliExpress Orders"
    ws.append(["Date", "Order ID", "Tracking ID", "Status", "Subject"])
    for item in orders:
        if item["type"] == "promo":
            continue
        ws.append([
            item["date"].strftime("%Y-%m-%d %H:%M") if hasattr(item["date"], "strftime") else str(item["date"]),
            item.get("order_id") or "",
            item.get("tracking_id") or "",
            item["status"],
            item["subject"],
        ])
    wb.save(output)
    total = sum(1 for i in orders if i["type"] == "transaction")
    print(f"Saved {total} orders to {output}")