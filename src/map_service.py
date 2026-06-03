"""
Bản đồ OSMnx + snap tọa độ lên node đường gần nhất (tránh đi xuyên hồ/sông).
"""

from __future__ import annotations

import pickle
from pathlib import Path

import osmnx as ox
from osmnx.distance import nearest_nodes


class MapService:
    def __init__(self, place_name: str, network_type: str, cache_dir: Path):
        self.place_name = place_name
        self.network_type = network_type
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self._graph = None
        self._node_coords = None

    @property
    def graph_path(self) -> Path:
        safe = self.place_name.replace(",", "").replace(" ", "_")[:80]
        return self.cache_dir / f"{safe}_{self.network_type}.pkl"

    def load_or_download(self, force_download: bool = False):
        if not force_download and self.graph_path.exists():
            with open(self.graph_path, "rb") as f:
                self._graph = pickle.load(f)
        else:
            print(f"[Map] Downloading OSM network: {self.place_name} ...")
            self._graph = ox.graph_from_place(
                self.place_name, network_type=self.network_type
            )
            self._graph = ox.add_edge_speeds(self._graph)
            self._graph = ox.add_edge_travel_times(self._graph)
            with open(self.graph_path, "wb") as f:
                pickle.dump(self._graph, f)
            print(f"[Map] Saved cache: {self.graph_path}")

        self._build_node_index()
        return self._graph

    def _build_node_index(self):
        g = self._graph
        self._node_coords = {
            n: (g.nodes[n]["y"], g.nodes[n]["x"]) for n in g.nodes
        }

    @property
    def graph(self):
        if self._graph is None:
            raise RuntimeError("Gọi load_or_download() trước.")
        return self._graph

    def nearest_node(self, lat: float, lon: float) -> int:
        """
        Snap (lat, lon) lên node đường gần nhất trên graph — không đi thẳng qua hồ nước.
        """
        return int(nearest_nodes(self.graph, lon, lat))

    def node_latlon(self, node_id: int) -> tuple[float, float]:
        return self._node_coords[node_id]

    def edge_count(self) -> int:
        return self.graph.number_of_edges()

    def node_count(self) -> int:
        return self.graph.number_of_nodes()
