"""
Xuat ban do tuong tac (HTML) — phong to / thu nho bang chuot hoac nut +/-.
"""

from __future__ import annotations

from pathlib import Path

import folium
from folium import plugins


def _node_latlon(graph, node_id: int) -> tuple[float, float]:
    return graph.nodes[node_id]["y"], graph.nodes[node_id]["x"]


def path_to_coords(graph, path_nodes: list[int]) -> list[tuple[float, float]]:
    return [_node_latlon(graph, n) for n in path_nodes]


def export_route_map(
    graph,
    path_nodes: list[int],
    shippers: list[dict],
    active_shipper: dict,
    input_lat: float,
    input_lon: float,
    order_id: str,
    route_info: dict,
    output_path: Path,
    show_all_shippers: bool = True,
) -> Path:
    """
    Tao file HTML (Folium + Leaflet) co the zoom/pan.
    Mo bang trinh duyet: double-click file hoac `start output/route_map.html`
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    route_coords = path_to_coords(graph, path_nodes)
    center_lat = sum(c[0] for c in route_coords) / len(route_coords)
    center_lon = sum(c[1] for c in route_coords) / len(route_coords)

    m = folium.Map(
        location=[center_lat, center_lon],
        zoom_start=15,
        tiles="OpenStreetMap",
        control_scale=True,
        zoom_control=True,
        scrollWheelZoom=True,
    )

    folium.TileLayer("CartoDB positron", name="CartoDB (sang)").add_to(m)
    folium.TileLayer("CartoDB dark_matter", name="CartoDB (toi)").add_to(m)

    route_fg = folium.FeatureGroup(name="Duong di", show=True)
    folium.PolyLine(
        route_coords,
        color="#2563eb",
        weight=6,
        opacity=0.85,
        popup=folium.Popup(
            f"<b>{order_id}</b><br>"
            f"Khoang cach: {route_info.get('distance_m')} m<br>"
            f"ETA: {route_info.get('eta_minutes')} phut<br>"
            f"Chang: {route_info.get('n_hops')}",
            max_width=280,
        ),
    ).add_to(route_fg)
    route_fg.add_to(m)

    # Diem nhap (chua snap)
    folium.Marker(
        [input_lat, input_lon],
        popup=f"Don {order_id} (nhap)",
        tooltip="Diem nhap",
        icon=folium.Icon(color="orange", icon="info-sign"),
    ).add_to(m)

    dest_lat, dest_lon = _node_latlon(graph, path_nodes[-1])
    folium.Marker(
        [dest_lat, dest_lon],
        popup="Diem dich (snap OSM)",
        tooltip="Dich",
        icon=folium.Icon(color="red", icon="flag"),
    ).add_to(m)

    origin_node = path_nodes[0]
    o_lat, o_lon = _node_latlon(graph, origin_node)
    folium.Marker(
        [o_lat, o_lon],
        popup=f"Shipper #{active_shipper['shipper_id']} (xuat phat)",
        tooltip=f"Shipper #{active_shipper['shipper_id']}",
        icon=folium.Icon(color="green", icon="play"),
    ).add_to(m)

    if show_all_shippers:
        shipper_fg = folium.FeatureGroup(name="Tat ca shipper", show=True)
        for s in shippers:
            sid = s["shipper_id"]
            color = "green" if sid == active_shipper["shipper_id"] else "blue"
            folium.Marker(
                [s["snap_lat"], s["snap_lon"]],
                popup=(
                    f"Shipper #{sid}<br>"
                    f"Node: {s.get('node_id')}<br>"
                    f"Lich su: {s.get('historical_orders')} don"
                ),
                tooltip=f"Shipper #{sid}",
                icon=folium.Icon(color=color, icon="user"),
            ).add_to(shipper_fg)
        shipper_fg.add_to(m)

    plugins.MiniMap(toggle_display=True, position="bottomright").add_to(m)
    plugins.Fullscreen(position="topright").add_to(m)

    title_html = (
        f'<div style="position:fixed;top:10px;left:50px;z-index:9999;'
        f"background:white;padding:8px 12px;border-radius:6px;"
        f'box-shadow:0 1px 4px rgba(0,0,0,.3);font-size:14px;">'
        f"<b>{order_id}</b> | Shipper #{active_shipper['shipper_id']} | "
        f"{route_info.get('distance_m')} m | ETA {route_info.get('eta_minutes')} phut"
        f"</div>"
    )
    m.get_root().html.add_child(folium.Element(title_html))

    folium.LayerControl(collapsed=False).add_to(m)

    m.save(str(output_path))
    return output_path


def export_route_map_png(
    graph,
    path_nodes: list[int],
    output_path: Path,
) -> Path | None:
    """Anh tinh PNG (khong zoom) — tuy chon."""
    try:
        import osmnx as ox
        import matplotlib.pyplot as plt
    except ImportError:
        return None

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig, ax = ox.plot_graph_route(
        graph,
        path_nodes,
        route_color="#2563eb",
        route_linewidth=4,
        node_size=0,
        bgcolor="#f8fafc",
        show=False,
        close=True,
        save=True,
        filepath=str(output_path),
    )
    plt.close(fig)
    return output_path
