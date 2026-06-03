# Đẩy lên GitHub

Repo local đã sẵn sàng tại `C:\Users\ThinkPad\smart-delivery-routing`.

## 1. Đăng nhập GitHub CLI (một lần)

```powershell
gh auth login
```

Chọn: GitHub.com → HTTPS → Login bằng trình duyệt.

## 2. Tạo repo public và push

```powershell
cd C:\Users\ThinkPad\smart-delivery-routing

gh repo create smart-delivery-routing --public --source=. --remote=origin --push --description "Demo giao hang: OSMnx, Open-Meteo, K-means 5 shipper, traffic sim"
```

## 3. (Tuỳ chọn) Đổi tên repo / tổ chức

```powershell
gh repo create YOUR_USERNAME/smart-delivery-routing --public --source=. --remote=origin --push
```

Sau khi push, cập nhật URL clone trong `README.md` thay `<your-user>` bằng username GitHub của bạn.
