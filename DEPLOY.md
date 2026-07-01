# Hướng dẫn Deploy NBK Salary lên Render + Neon (Miễn phí)

## Tổng quan
- **Frontend**: React build tĩnh, serve từ backend FastAPI
- **Backend**: FastAPI trên Render (free tier)
- **Database**: Neon PostgreSQL (free tier vĩnh viễn, 0.5GB)
- **Chi phí**: $0/tháng
- **Không cần**: thẻ tín dụng, renew token

---

## Bước 1: Tạo Database trên Neon (5 phút)

1. Vào https://neon.tech → Sign up bằng GitHub/Google
2. Tạo project mới:
   - Project name: `nbk-salary`
   - Region: `Asia Pacific (Singapore)`
3. Copy **Connection string** (dạng):
   ```
   postgresql://username:password@ep-xxx.ap-southeast-1.aws.neon.tech/neondb?sslmode=require
   ```
4. Giữ lại connection string này cho Bước 2

---

## Bước 2: Push code lên GitHub

```bash
cd "d:\NBK\Tinh luong"
git init
git add .
git commit -m "Initial deploy"
git remote add origin https://github.com/YOUR_USERNAME/nbk-salary.git
git push -u origin main
```

---

## Bước 3: Deploy lên Render (5 phút)

1. Vào https://render.com → Sign up bằng GitHub
2. Click **New** → **Web Service**
3. Connect GitHub repo `nbk-salary`
4. Cấu hình:
   - **Name**: `nbk-salary`
   - **Region**: `Singapore`
   - **Runtime**: `Python 3`
   - **Build Command**: `./build.sh`
   - **Start Command**: `./start.sh`
   - **Plan**: `Free`
5. Thêm Environment Variables:
   - `DATABASE_URL` = (paste Neon connection string từ Bước 1)
   - `SECRET_KEY` = (tự generate hoặc nhập chuỗi random dài)
   - `CORS_ORIGINS` = `["*"]`
   - `DEBUG` = `False`
   - `NODE_VERSION` = `18`
   - `PYTHON_VERSION` = `3.11.0`
6. Click **Create Web Service**
7. Đợi build ~5 phút

---

## Bước 4: Truy cập

- URL: `https://nbk-salary.onrender.com`
- Tài khoản mặc định (từ seed):
  - Username: `admin`
  - Password: `Admin@123`

---

## Lưu ý

### Free tier Render:
- Service sẽ sleep sau 15 phút không hoạt động
- Lần đầu truy cập sau khi sleep sẽ chờ ~30 giây để wake up
- Không giới hạn bandwidth hay request

### Free tier Neon:
- 0.5GB storage (đủ cho ~vài nghìn NV)
- Compute auto-sleep sau 5 phút idle
- Vĩnh viễn miễn phí, không xóa data

### Cập nhật code:
- Push lên GitHub → Render tự động re-deploy

---

## Troubleshooting

### Lỗi database connection:
- Kiểm tra DATABASE_URL có `?sslmode=require` ở cuối
- Đảm bảo Neon project đang active

### Lỗi build frontend:
- Đảm bảo `NODE_VERSION=18` trong env vars

### Xem logs:
- Render Dashboard → Service → Logs
