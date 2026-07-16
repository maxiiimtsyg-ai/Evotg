from sqlalchemy import func
from datetime import datetime, timezone

from database import SessionLocal
from models import Receipt, ReceiptItem


def today_stats():

    db = SessionLocal()

    try:

        today = datetime.now(timezone.utc).date()

        receipts = (
            db.query(Receipt)
            .filter(func.date(Receipt.date) == today)
            .all()
        )

        total = sum(r.amount for r in receipts)
        checks = len(receipts)

        average = round(total / checks, 2) if checks else 0

        return {
            "total": round(total, 2),
            "checks": checks,
            "average": average
        }

    finally:
        db.close()


def top_products(limit=10):

    db = SessionLocal()

    try:

        rows = (
            db.query(
                ReceiptItem.name,
                func.count(ReceiptItem.id)
            )
            .group_by(
                ReceiptItem.name
            )
            .order_by(
                func.count(ReceiptItem.id).desc()
            )
            .limit(limit)
            .all()
        )

        return rows

    finally:
        db.close()
