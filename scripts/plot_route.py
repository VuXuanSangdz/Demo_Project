#!/usr/bin/env python3
"""
Xuat ban do tuong tac (HTML) co zoom/pan.

Vi du:
  python scripts/plot_route.py
  python scripts/plot_route.py --lat 21.0278 --lon 105.8355 --order ORD-001
  python scripts/plot_route.py --png
"""

from __future__ import annotations

import argparse
import sys
import webbrowser
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src.clustering import assign_order_to_shipper, load_clusters
from src.config_loader import load_config, resolve_path
from src.map_service import MapService
from src.map_visualizer import export_route_map, export_route_map_png
from src.routing import shortest_delivery_route
from src.traffic_simulator import TrafficSimulator
from src.weather_service import WeatherService


def parse_args():
    p = argparse.ArgumentParser(description="Xuat ban do lo trinh (HTML zoom duoc)")
    p.add_argument("--lat", type=float, default=21.0278, help="Vi do don")
    p.add_argument("--lon", type=float, default=105.8355, help="Kinh do don")
    p.add_argument("--order", default="ORD-MAP-001", help="Ma don")
    p.add_argument(
        "--out",
        default="output/route_map.html",
        help="Duong dan file HTML",
    )
    p.add_argument("--png", action="store_true", help="Them xuat PNG tinh")
    p.add_argument("--open", action="store_true", help="Mo file HTML sau khi tao")
    return p.parse_args()


def main():
    args = parse_args()
    cfg = load_config()

    map_svc = MapService(
        cfg["place_name"],
        cfg["network_type"],
        resolve_path(cfg["paths"]["graph_cache"]),
    )
    map_svc.load_or_download()

    shippers = load_clusters(resolve_path(cfg["paths"]["shipper_clusters"]))
    traffic = TrafficSimulator(cfg["traffic"])
    weather = WeatherService(cfg["latitude"], cfg["longitude"], cfg["weather"])

    lat, lon = args.lat, args.lon
    dest_node = map_svc.nearest_node(lat, lon)
    shipper = assign_order_to_shipper(lat, lon, shippers)
    origin_node = shipper["node_id"]
    if origin_node is None:
        origin_node = map_svc.nearest_node(shipper["snap_lat"], shipper["snap_lon"])

    result = shortest_delivery_route(
        map_svc, traffic, weather, origin_node, dest_node
    )
    if not result.get("ok"):
        print(f"Loi dinh tuyen: {result.get('message')}")
        return 1

    out_html = resolve_path(args.out)
    export_route_map(
        map_svc.graph,
        result["path_nodes"],
        shippers,
        shipper,
        lat,
        lon,
        args.order,
        result,
        out_html,
    )
    print(f"[Map] HTML (zoom/pan): {out_html.resolve()}")

    if args.png:
        out_png = out_html.with_suffix(".png")
        png = export_route_map_png(map_svc.graph, result["path_nodes"], out_png)
        if png:
            print(f"[Map] PNG: {png.resolve()}")

    print(
        f"  Shipper #{shipper['shipper_id']} | "
        f"{result['distance_m']} m | ETA {result['eta_minutes']} phut"
    )
    print("  Mo file HTML trong Chrome/Edge de dung chuot zoom.")

    if args.open:
        webbrowser.open(out_html.resolve().as_uri())

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
