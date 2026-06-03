"""
Mô phỏng giao thông: phạt tuyến primary/secondary và khung giờ cao điểm.
"""

from __future__ import annotations

from datetime import datetime


class TrafficSimulator:
    def __init__(self, traffic_cfg: dict):
        self.cfg = traffic_cfg

    def is_peak_hour(self, dt: datetime | None = None) -> bool:
        dt = dt or datetime.now()
        hour = dt.hour
        for start, end in self.cfg.get("peak_hours", [[7, 9], [17, 19]]):
            if start <= hour < end:
                return True
        return False

    def edge_weight_multiplier(
        self, edge_data: dict, dt: datetime | None = None
    ) -> float:
        mult = 1.0
        highway = edge_data.get("highway", "")
        if isinstance(highway, list):
            highway = highway[0] if highway else ""

        major_tags = set(self.cfg.get("highway_tags", []))
        secondary_tags = set(self.cfg.get("secondary_tags", []))

        if highway in major_tags:
            mult *= self.cfg.get("major_road_multiplier", 1.45)
        elif highway in secondary_tags:
            mult *= self.cfg.get("secondary_road_multiplier", 1.25)

        if self.is_peak_hour(dt):
            mult *= self.cfg.get("peak_multiplier", 1.35)

        return mult

    def describe(self, dt: datetime | None = None) -> str:
        dt = dt or datetime.now()
        peak = "cao điểm" if self.is_peak_hour(dt) else "bình thường"
        return (
            f"Khung giờ {dt.strftime('%H:%M')} — {peak}; "
            f"phạt tuyến lớn x{self.cfg.get('major_road_multiplier', 1.45)}, "
            f"phụ x{self.cfg.get('secondary_road_multiplier', 1.25)}"
        )
