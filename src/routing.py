"""
Định tuyến ngắn nhất trên graph OSM với trọng số giao thông + thời tiết.
"""

from __future__ import annotations

from datetime import datetime

import networkx as nx

from src.map_service import MapService
from src.traffic_simulator import TrafficSimulator
from src.weather_service import WeatherService


def build_weighted_graph(
    G: nx.MultiDiGraph,
    traffic: TrafficSimulator,
    weather_factor: float,
    dt: datetime | None = None,
) -> nx.DiGraph:
    """Tạo graph có trọng số travel_time đã nhân hệ số."""
    H = nx.DiGraph()
    for u, v, key, data in G.edges(keys=True, data=True):
        base_time = data.get("travel_time", data.get("length", 1) / 13.89)
        mult = traffic.edge_weight_multiplier(data, dt)
        weight = base_time * mult * weather_factor
        if H.has_edge(u, v):
            if H[u][v]["weight"] > weight:
                H[u][v]["weight"] = weight
        else:
            H.add_edge(u, v, weight=weight)
    return H


def shortest_delivery_route(
    map_svc: MapService,
    traffic: TrafficSimulator,
    weather: WeatherService,
    origin_node: int,
    dest_node: int,
    dt: datetime | None = None,
) -> dict:
    dt = dt or datetime.now()
    w_factor, weather_note = weather.travel_time_factor()
    G = map_svc.graph
    H = build_weighted_graph(G, traffic, w_factor, dt)

    try:
        path = nx.shortest_path(H, origin_node, dest_node, weight="weight")
        length_m = nx.shortest_path_length(
            G, origin_node, dest_node, weight="length"
        )
        time_s = sum(
            H[path[i]][path[i + 1]]["weight"]
            for i in range(len(path) - 1)
        )
    except nx.NetworkXNoPath:
        return {
            "ok": False,
            "message": "Không tìm thấy đường đi trên mạng lưới (có thể do đứt graph).",
        }

    return {
        "ok": True,
        "path_nodes": path,
        "distance_m": round(length_m, 1),
        "eta_minutes": round(time_s / 60, 1),
        "weather_factor": w_factor,
        "weather_note": weather_note,
        "traffic_note": traffic.describe(dt),
        "n_hops": len(path) - 1,
    }
