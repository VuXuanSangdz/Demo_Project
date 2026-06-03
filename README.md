# Demo Project — Smart Delivery Routing

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

Demo Python mô phỏng hệ thống giao hàng thông minh tại **Quận 1, TP.HCM**: bản đồ **OSMnx**, thời tiết **Open-Meteo**, giao thông giả lập, phân cụm **K-means** (5 shipper) và nhập đơn mới từ bàn phím.

**Repository:** [github.com/VuXuanSangdz/Demo_Project](https://github.com/VuXuanSangdz/Demo_Project)

## Tính năng

| Thành phần | Mô tả |
|------------|--------|
| **OSMnx** | Tải mạng lưới đường `drive` từ OpenStreetMap, cache pickle |
| **Nearest node** | Snap tọa độ lên **node đường** gần nhất — tránh đường thẳng xuyên hồ/sông |
| **Open-Meteo** | Hệ số ETA theo mưa, gió (API miễn phí) |
| **Traffic sim** | Phạt `primary`/`secondary` và khung giờ cao điểm (7–9h, 17–19h) |
| **K-means** | ~1200 đơn lịch sử → 5 tâm cụm → vị trí shipper |
| **CLI** | Nhập `lat`/`lon` đơn mới, gán shipper, tính đường ngắn nhất |

## Cấu trúc dự án

```
smart-delivery-routing/
├── config.yaml              # Khu vực, tham số traffic/weather
├── main.py                  # Entry point demo
├── requirements.txt
├── data/
│   ├── historical_orders.csv   # 1200 đơn (có sẵn)
│   ├── shipper_clusters.json   # 5 shipper (preview / sau train OSM)
│   ├── traffic_config.json
│   └── graph/                  # Cache OSMnx (*.pkl, gitignore)
├── scripts/
│   ├── generate_historical_data.py
│   ├── generate_shipper_preview.py
│   ├── download_graph.py
│   └── train_clusters.py
├── src/
│   ├── map_service.py
│   ├── weather_service.py
│   ├── traffic_simulator.py
│   ├── clustering.py
│   ├── routing.py
│   └── demo.py
└── output/                  # delivery_log.jsonl
```

## Yêu cầu

- Python 3.10+
- Kết nối Internet (lần đầu: tải OSM + Open-Meteo)

## Cài đặt

```bash
git clone https://github.com/VuXuanSangdz/Demo_Project.git
cd Demo_Project
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS/Linux
source .venv/bin/activate

pip install -r requirements.txt
```

## Chạy nhanh

### Bước 1 — Tải bản đồ OSM (một lần, ~1–3 phút)

```bash
python scripts/download_graph.py
```

### Bước 2 — Snap 5 shipper lên node đường (tránh hồ nước)

```bash
python scripts/train_clusters.py
```

### Bước 3 — Chạy demo tương tác

```bash
python main.py
```

Nhập tọa độ mẫu trong Quận 1:

| Điểm | lat | lon |
|------|-----|-----|
| Chợ Bến Thành (gần) | 10.7720 | 106.6980 |
| Nhà thờ Đức Bà | 10.7798 | 106.6992 |
| Bưu điện Sài Gòn | 10.7800 | 106.7004 |

Trong CLI:

- **Enter** — nhập đơn mới
- **retrain** — huấn luyện lại K-means
- **q** — thoát

## Dữ liệu có sẵn

- `data/historical_orders.csv` — 1200 bản ghi (`order_id`, `lat`, `lon`, `created_at`, `weight_kg`, `priority`)
- `data/shipper_clusters.json` — preview từ K-means; sau `train_clusters.py` có `node_id` OSM thật
- `data/traffic_config.json` — tham số phạt tuyến và giờ cao điểm

Tạo lại dữ liệu lịch sử:

```bash
python scripts/generate_historical_data.py
python scripts/generate_shipper_preview.py
```

## Thuật toán

### 1. Nearest node (tránh hồ)

```python
from osmnx.distance import nearest_nodes
node_id = nearest_nodes(graph, lon, lat)
```

Điểm đích và tâm cụm shipper đều được **snap** lên mạng lưới đường — đường đi thực tế bám OSM, không nối thẳng qua vùng không có đường.

### 2. K-means → 5 shipper

- Input: `(lat, lon)` từ lịch sử
- `KMeans(n_clusters=5)`
- Mỗi tâm cụm → `nearest_node` → `snap_lat`, `snap_lon`, `node_id`

### 3. Gán đơn mới

Shipper có khoảng cách Euclidean nhỏ nhất tới `(snap_lat, snap_lon)` (sau khi đã snap OSM).

### 4. Định tuyến

- Trọng số cạnh = `travel_time × traffic_mult × weather_factor`
- `networkx.shortest_path` trên graph có trọng số

## Cấu hình

Chỉnh `config.yaml`:

- `place_name` — vùng OSMnx
- `traffic.peak_hours`, `major_road_multiplier`, …
- `weather.rain_factor`, …

## API & nguồn dữ liệu

- [OSMnx](https://osmnx.readthedocs.io/) — OpenStreetMap
- [Open-Meteo](https://open-meteo.com/) — không cần API key

## Giới hạn demo

- Một khu vực nhỏ (Quận 1) để graph gọn
- Giao thông **giả lập**, không phải Google Maps Traffic
- Gán shipper theo khoảng cách tâm cụm, chưa tối ưu VRP đầy đủ

## License

MIT — xem [LICENSE](LICENSE).
