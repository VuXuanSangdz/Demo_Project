#!/usr/bin/env python3
"""
Sinh ~1200 đơn hàng lịch sử ngẫu nhiên trong bbox Quận 1 TP.HCM.
Chạy: python scripts/generate_historical_data.py
"""

import csv
import random
from datetime import datetime, timedelta
from pathlib import Path

# Bbox Quận 1 + vùng lân cận (tránh vùng sông rộng)
LAT_MIN, LAT_MAX = 10.758, 10.795
LON_MIN, LON_MAX = 106.678, 106.715

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "data" / "historical_orders.csv"
N_ORDERS = 1200
SEED = 42


def main():
    random.seed(SEED)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    base = datetime(2025, 1, 1, 8, 0, 0)

    rows = []
    for i in range(1, N_ORDERS + 1):
        lat = round(random.uniform(LAT_MIN, LAT_MAX), 6)
        lon = round(random.uniform(LON_MIN, LON_MAX), 6)
        ts = base + timedelta(
            days=random.randint(0, 180),
            hours=random.randint(6, 22),
            minutes=random.randint(0, 59),
        )
        rows.append(
            {
                "order_id": f"ORD-{i:05d}",
                "lat": lat,
                "lon": lon,
                "created_at": ts.isoformat(),
                "weight_kg": round(random.uniform(0.3, 8.0), 2),
                "priority": random.choice(["normal", "express"]),
            }
        )

    with open(OUT, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(
            f,
            fieldnames=[
                "order_id",
                "lat",
                "lon",
                "created_at",
                "weight_kg",
                "priority",
            ],
        )
        w.writeheader()
        w.writerows(rows)

    print(f"Created {len(rows)} orders -> {OUT}")


if __name__ == "__main__":
    main()
