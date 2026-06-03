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

git remote add origin https://github.com/VuXuanSangdz/Demo_Project.git
git branch -M main
git push -u origin main
```

## 3. (Tuỳ chọn) Đổi tên repo / tổ chức

```powershell
gh repo create YOUR_USERNAME/smart-delivery-routing --public --source=. --remote=origin --push
```

Sau khi push, cập nhật URL clone trong `README.md` thay `<your-user>` bằng username GitHub của bạn.
