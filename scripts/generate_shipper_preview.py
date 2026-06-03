#!/usr/bin/env python3
"""K-means preview (khong can OSMnx) — dung khi chua tai graph."""

import json
import sys
from pathlib import Path

import pandas as pd
from sklearn.cluster import KMeans

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src.config_loader import load_config, resolve_path


def main():
    cfg = load_config()
    df = pd.read_csv(resolve_path(cfg["paths"]["historical_orders"]))
    km = KMeans(n_clusters=cfg["n_clusters"], random_state=cfg["random_state"], n_init=10)
    labels = km.fit_predict(df[["lat", "lon"]])
    shippers = []
    for i in range(cfg["n_clusters"]):
        clat, clon = km.cluster_centers_[i]
        n = int((labels == i).sum())
        shippers.append(
            {
                "shipper_id": i + 1,
                "cluster_center_lat": round(float(clat), 6),
                "cluster_center_lon": round(float(clon), 6),
                "node_id": None,
                "snap_lat": round(float(clat), 6),
                "snap_lon": round(float(clon), 6),
                "historical_orders": n,
                "note": "Preview — chay train_clusters.py sau khi tai graph de snap node OSM",
            }
        )
    out = resolve_path(cfg["paths"]["shipper_clusters"])
    with open(out, "w", encoding="utf-8") as f:
        json.dump({"shippers": shippers, "n_clusters": len(shippers)}, f, indent=2)
    print(f"Saved preview -> {out}")


if __name__ == "__main__":
    main()
