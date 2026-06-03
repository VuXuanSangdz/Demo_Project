#!/usr/bin/env python3
"""Chay mot don mau (khong tuong tac) de xem ket qua."""

import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src.clustering import assign_order_to_shipper, load_clusters, load_historical_orders
from src.config_loader import load_config, resolve_path
from src.map_service import MapService
from src.map_visualizer import export_route_map
from src.routing import shortest_delivery_route
from src.traffic_simulator import TrafficSimulator
from src.weather_service import WeatherService


def main():
    cfg = load_config()
    print("=" * 60)
    print("  DEMO SAMPLE — Quan Dong Da, Ha Noi")
    print("=" * 60)

    map_svc = MapService(
        cfg["place_name"],
        cfg["network_type"],
        resolve_path(cfg["paths"]["graph_cache"]),
    )
    map_svc.load_or_download()
    print(f"[Map] Nodes: {map_svc.node_count()}, Edges: {map_svc.edge_count()}")

    df = load_historical_orders(resolve_path(cfg["paths"]["historical_orders"]))
    shippers = load_clusters(resolve_path(cfg["paths"]["shipper_clusters"]))
    print(f"[Data] Historical orders: {len(df)}")
    print("\n--- 5 Shipper (K-means + OSM snap) ---")
    for s in shippers:
        print(
            f"  #{s['shipper_id']}: node {s['node_id']} "
            f"({s['snap_lat']}, {s['snap_lon']}) — {s['historical_orders']} don"
        )

    traffic = TrafficSimulator(cfg["traffic"])
    weather = WeatherService(cfg["latitude"], cfg["longitude"], cfg["weather"])
    print(f"\n[Traffic] {traffic.describe()}")
    try:
        w_factor, w_note = weather.travel_time_factor()
        print(f"[Weather] {w_note}")
    except Exception as e:
        print(f"[Weather] API error: {e}")
        w_factor = 1.0

    # Don mau: Van Mieu — Quoc Tu Giam
    order_id = "ORD-DEMO-001"
    lat, lon = 21.0278, 105.8355
    print(f"\n--- Don moi: {order_id} @ ({lat}, {lon}) ---")

    dest_node = map_svc.nearest_node(lat, lon)
    dest_lat, dest_lon = map_svc.node_latlon(dest_node)
    shipper = assign_order_to_shipper(lat, lon, shippers)
    origin_node = shipper["node_id"]

    print(f"  Snap dich: node {dest_node} ({dest_lat:.6f}, {dest_lon:.6f})")
    print(f"  Shipper: #{shipper['shipper_id']} @ node {origin_node}")

    result = shortest_delivery_route(
        map_svc, traffic, weather, origin_node, dest_node
    )
    if not result.get("ok"):
        print(f"  LOI: {result.get('message')}")
        return 1

    print("\n  === KET QUA DINH TUYEN ===")
    print(f"  Khoang cach: {result['distance_m']} m")
    print(f"  ETA: {result['eta_minutes']} phut")
    print(f"  So chang: {result['n_hops']}")
    print(f"  {result['traffic_note']}")
    print(f"  {result['weather_note']}")

    map_html = resolve_path("output/route_map.html")
    export_route_map(
        map_svc.graph,
        result["path_nodes"],
        shippers,
        shipper,
        lat,
        lon,
        order_id,
        result,
        map_html,
    )
    print(f"\n[Map] Mo file de zoom/pan: {map_html.resolve()}")
    print("=" * 60)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
