"""
Demo tương tác: huấn luyện K-means, nhập đơn mới từ bàn phím, định tuyến.
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

from src.clustering import (
    assign_order_to_shipper,
    load_clusters,
    load_historical_orders,
    save_clusters,
    train_shipper_clusters,
)
from src.config_loader import load_config, resolve_path
from src.map_service import MapService
from src.routing import shortest_delivery_route
from src.traffic_simulator import TrafficSimulator
from src.weather_service import WeatherService


def _prompt_float(label: str) -> float:
    while True:
        raw = input(f"  {label}: ").strip().replace(",", ".")
        try:
            return float(raw)
        except ValueError:
            print("    → Nhập số hợp lệ (vd: 21.0194)")


def _print_shippers(shippers: list[dict]):
    print("\n--- 5 vị trí Shipper (tâm K-means + snap node OSM) ---")
    for s in shippers:
        print(
            f"  Shipper #{s['shipper_id']}: node={s['node_id']} "
            f"({s['snap_lat']}, {s['snap_lon']}) — "
            f"{s['historical_orders']} đơn lịch sử"
        )


def run_demo():
    cfg = load_config()
    print("=" * 60)
    print("  SMART DELIVERY ROUTING DEMO")
    print("  OSMnx | Open-Meteo | Traffic sim | K-means (5 shipper)")
    print("=" * 60)

    map_svc = MapService(
        cfg["place_name"],
        cfg["network_type"],
        resolve_path(cfg["paths"]["graph_cache"]),
    )
    map_svc.load_or_download()
    print(
        f"\n[Map] Graph: {map_svc.node_count()} nodes, "
        f"{map_svc.edge_count()} edges"
    )

    hist_path = resolve_path(cfg["paths"]["historical_orders"])
    cluster_path = resolve_path(cfg["paths"]["shipper_clusters"])

    df = load_historical_orders(hist_path)
    print(f"[Data] Lịch sử đơn hàng: {len(df)} bản ghi từ {hist_path.name}")

    if cluster_path.exists():
        shippers = load_clusters(cluster_path)
        print(f"[Cluster] Đã load {len(shippers)} shipper từ cache.")
    else:
        print("[Cluster] Huấn luyện K-means...")
        shippers = train_shipper_clusters(
            df,
            map_svc,
            n_clusters=cfg["n_clusters"],
            random_state=cfg["random_state"],
        )
        save_clusters(shippers, cluster_path)
        print(f"[Cluster] Đã lưu: {cluster_path}")

    _print_shippers(shippers)

    traffic = TrafficSimulator(cfg["traffic"])
    weather = WeatherService(cfg["latitude"], cfg["longitude"], cfg["weather"])

    print(f"\n[Traffic] {traffic.describe()}")
    try:
        w_factor, w_note = weather.travel_time_factor()
        print(f"[Weather] {w_note}")
    except Exception as e:
        print(f"[Weather] Không lấy được API (offline?): {e}")
        w_factor = 1.0

    print("\n" + "-" * 60)
    print("Nhap don moi (lat/lon trong khu vuc Quan Dong Da, Ha Noi)")
    print("Gõ 'q' để thoát, 'retrain' để huấn luyện lại K-means")
    print("-" * 60)

    while True:
        cmd = input("\nLệnh [Enter=đơn mới / q / retrain]: ").strip().lower()
        if cmd == "q":
            print("Tạm biệt.")
            break
        if cmd == "retrain":
            shippers = train_shipper_clusters(
                df, map_svc, cfg["n_clusters"], cfg["random_state"]
            )
            save_clusters(shippers, cluster_path)
            _print_shippers(shippers)
            continue

        order_id = input("  Mã đơn (vd: ORD-NEW-001): ").strip() or "ORD-NEW"
        lat = _prompt_float("Vĩ độ lat")
        lon = _prompt_float("Kinh độ lon")

        dest_node = map_svc.nearest_node(lat, lon)
        dest_lat, dest_lon = map_svc.node_latlon(dest_node)
        shipper = assign_order_to_shipper(lat, lon, shippers)

        print(f"\n  → Snap đích: node {dest_node} ({dest_lat:.6f}, {dest_lon:.6f})")
        print(
            f"  → Shipper được gán: #{shipper['shipper_id']} "
            f"tại ({shipper['snap_lat']}, {shipper['snap_lon']})"
        )

        origin_node = shipper.get("node_id")
        if origin_node is None:
            print(
                "  [!] Shipper chua snap OSM — dang tim node gan tam cum..."
            )
            origin_node = map_svc.nearest_node(
                shipper["snap_lat"], shipper["snap_lon"]
            )
        result = shortest_delivery_route(
            map_svc, traffic, weather, origin_node, dest_node
        )

        if not result.get("ok"):
            print(f"  ✗ {result.get('message')}")
            continue

        print("\n  === KẾT QUẢ ĐỊNH TUYẾN ===")
        print(f"  Khoảng cách (đường bộ): {result['distance_m']} m")
        print(f"  ETA (có traffic + thời tiết): {result['eta_minutes']} phút")
        print(f"  Số chặng: {result['n_hops']}")
        print(f"  {result['traffic_note']}")
        print(f"  {result['weather_note']}")

        log = {
            "order_id": order_id,
            "input_lat": lat,
            "input_lon": lon,
            "dest_node": dest_node,
            "shipper_id": shipper["shipper_id"],
            "timestamp": datetime.now().isoformat(),
            **{k: result[k] for k in ("distance_m", "eta_minutes", "n_hops")},
        }
        out_dir = resolve_path("output")
        out_dir.mkdir(exist_ok=True)
        log_file = out_dir / "delivery_log.jsonl"
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(log, ensure_ascii=False) + "\n")
        print(f"  (đã ghi log → {log_file})")


if __name__ == "__main__":
    run_demo()
