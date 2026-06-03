#!/usr/bin/env python3
"""Huấn luyện K-means và lưu 5 vị trí shipper (cần graph đã tải)."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src.clustering import (
    load_historical_orders,
    save_clusters,
    train_shipper_clusters,
)
from src.config_loader import load_config, resolve_path
from src.map_service import MapService


def main():
    cfg = load_config()
    map_svc = MapService(
        cfg["place_name"],
        cfg["network_type"],
        resolve_path(cfg["paths"]["graph_cache"]),
    )
    map_svc.load_or_download()
    df = load_historical_orders(resolve_path(cfg["paths"]["historical_orders"]))
    shippers = train_shipper_clusters(
        df, map_svc, cfg["n_clusters"], cfg["random_state"]
    )
    out = resolve_path(cfg["paths"]["shipper_clusters"])
    save_clusters(shippers, out)
    for s in shippers:
        print(s)


if __name__ == "__main__":
    main()
