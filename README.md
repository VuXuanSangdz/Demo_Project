# Demo Project — Smart Delivery Routing

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

Demo Python mô phỏng hệ thống giao hàng thông minh tại **Quận Đống Đa, Hà Nội**: bản đồ **OSMnx**, thời tiết **Open-Meteo**, giao thông giả lập, phân cụm **K-means** (5 shipper) và nhập đơn mới từ bàn phím.

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
| **Bản đồ HTML** | `scripts/plot_route.py` — zoom/pan trong trình duyệt (Folium) |

## Cấu trúc dự án

```
Demo_Project/
├── config.yaml                 # Khu vực, traffic, weather (một file cấu hình)
├── main.py                     # Demo CLI — nhập đơn
├── setup.bat / run.bat         # Windows: cài đặt / chạy demo
├── plot_map.bat                # Windows: xuất & mở bản đồ HTML
├── requirements.txt
├── data/
│   ├── historical_orders.csv   # ~1200 đơn lịch sử
│   ├── shipper_clusters.json   # 5 shipper (sau train_clusters.py)
│   └── graph/                    # Cache OSMnx (*.pkl, không đẩy Git)
├── scripts/
│   ├── download_graph.py       # Tải bản đồ OSM
│   ├── train_clusters.py         # K-means + snap node OSM
│   ├── plot_route.py           # Xuất bản đồ zoom (HTML)
│   ├── generate_historical_data.py
│   └── generate_shipper_preview.py  # Preview cluster (không cần OSM)
├── src/
│   ├── demo.py                 # Logic CLI
│   ├── map_service.py          # OSMnx + nearest node
│   ├── map_visualizer.py       # Folium HTML
│   ├── weather_service.py      # Open-Meteo
│   ├── traffic_simulator.py
│   ├── clustering.py
│   └── routing.py
└── output/                     # route_map.html, delivery_log.jsonl
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

**Windows (PowerShell) — khuyến nghị, một lệnh cài đủ:**

```powershell
cd C:\Users\ThinkPad\Downloads\Demo_Project-main   # đổi đường dẫn nếu clone ở chỗ khác
.\install.ps1
```

Script tự làm: tạo `.venv` → cài `osmnx`, `folium`, … → tải bản đồ OSM → huấn luyện 5 shipper.

> **Lưu ý PowerShell:** phải gõ `.\setup.bat`, `.\run.bat` (có dấu `.\` ở đầu).  
> Không gõ `setup.bat` trần — sẽ báo lỗi *not recognized*.

**Windows (từng bước):**

```powershell
.\setup.bat
.venv\Scripts\python.exe scripts\download_graph.py
.venv\Scripts\python.exe scripts\train_clusters.py
.\run.bat
```

**Windows (nhanh):** sau `install.ps1` → `.\run.bat`.

## Chạy nhanh

### Bước 1 — Tải bản đồ OSM (một lần, ~1–3 phút)

Nếu bạn đã từng chạy bản Quận 1 TP.HCM, xóa file `.pkl` cũ trong `data/graph/` trước khi tải lại.

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

Nhập tọa độ mẫu trong Quận Đống Đa:

| Điểm | lat | lon |
|------|-----|-----|
| Văn Miếu — Quốc Tử Giám | 21.0278 | 105.8355 |
| Hồ Đắc Di | 21.0130 | 105.8260 |
| Khu vực Ô Chợ Dừa | 21.0190 | 105.8250 |

### Bản đồ tương tác (phóng to / thu nhỏ)

```bash
python scripts/plot_route.py --open
```

Tạo `output/route_map.html` — mở bằng Chrome/Edge:

- **Scroll chuột** hoặc nút **+ / −** để zoom
- Kéo để pan; góc phải có **MiniMap** và **Fullscreen**
- Đổi lớp nền: OpenStreetMap / CartoDB trong Layer Control

Sau mỗi đơn trong `main.py`, file `output/route_map.html` được cập nhật tự động.

Trong CLI:

- **Enter** — nhập đơn mới
- **retrain** — huấn luyện lại K-means
- **q** — thoát

## Dữ liệu có sẵn

- `data/historical_orders.csv` — 1200 bản ghi (`order_id`, `lat`, `lon`, …)
- `data/shipper_clusters.json` — sau `train_clusters.py` có `node_id` OSM thật
- Tham số giao thông / thời tiết: trong `config.yaml` (mục `traffic`, `weather`)

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

- Một khu vực nhỏ (Quận Đống Đa) để graph gọn
- Giao thông **giả lập**, không phải Google Maps Traffic
- Gán shipper theo khoảng cách tâm cụm, chưa tối ưu VRP đầy đủ

## License

MIT — xem [LICENSE](LICENSE).
