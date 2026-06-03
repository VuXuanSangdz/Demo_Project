"""
K-means trên lịch sử đơn hàng → 5 tâm cụm → snap lên node OSM (shipper).
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.cluster import KMeans

from src.map_service import MapService


def load_historical_orders(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path)
    required = {"order_id", "lat", "lon"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"Thiếu cột trong CSV: {missing}")
    return df


def train_shipper_clusters(
    df: pd.DataFrame,
    map_svc: MapService,
    n_clusters: int = 5,
    random_state: int = 42,
) -> list[dict]:
    coords = df[["lat", "lon"]].values
    kmeans = KMeans(n_clusters=n_clusters, random_state=random_state, n_init=10)
    labels = kmeans.fit_predict(coords)
    df = df.copy()
    df["cluster"] = labels

    shippers = []
    for i in range(n_clusters):
        center_lat, center_lon = kmeans.cluster_centers_[i]
        node_id = map_svc.nearest_node(center_lat, center_lon)
        snap_lat, snap_lon = map_svc.node_latlon(node_id)
        cluster_orders = int((labels == i).sum())
        shippers.append(
            {
                "shipper_id": i + 1,
                "cluster_center_lat": round(float(center_lat), 6),
                "cluster_center_lon": round(float(center_lon), 6),
                "node_id": int(node_id),
                "snap_lat": round(snap_lat, 6),
                "snap_lon": round(snap_lon, 6),
                "historical_orders": cluster_orders,
            }
        )
    return shippers


def save_clusters(shippers: list[dict], path: Path):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump({"shippers": shippers, "n_clusters": len(shippers)}, f, indent=2)


def load_clusters(path: Path) -> list[dict]:
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    return data["shippers"]


def assign_order_to_shipper(
    lat: float, lon: float, shippers: list[dict]
) -> dict:
    """Gán đơn mới cho shipper có tâm cụm (đã snap) gần nhất."""
    best = None
    best_dist = float("inf")
    for s in shippers:
        d = (lat - s["snap_lat"]) ** 2 + (lon - s["snap_lon"]) ** 2
        if d < best_dist:
            best_dist = d
            best = s
    return best
