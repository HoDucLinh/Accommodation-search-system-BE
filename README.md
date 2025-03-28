# 🏠 Hệ Thống Tìm Kiếm Chỗ Ở - Backend

*✨ Hệ thống tìm kiếm chỗ ở mạnh mẽ, tiện lợi và hiện đại ✨*

---

## 📖 Giới Thiệu
Đây là repository chứa mã nguồn **backend** của *Hệ Thống Tìm Kiếm Chỗ Ở*, một nền tảng được thiết kế để hỗ trợ người dùng trong việc tìm kiếm, quản lý và tương tác với các danh sách chỗ ở như nhà trọ, căn hộ, khách sạn, nhà nghỉ, v.v. 🎯 Backend này được xây dựng bằng **Python** và **Django Framework**, sử dụng **MySQL** làm cơ sở dữ liệu, cung cấp các API mạnh mẽ để xử lý dữ liệu, xác thực người dùng và hỗ trợ tìm kiếm nâng cao.

Mục tiêu của dự án là tạo ra một hệ thống **đáng tin cậy**, **dễ bảo trì** và **tích hợp mượt mà** với frontend, mang lại trải nghiệm tuyệt vời cho người dùng cuối. 🚀

---

## 🌟 Tính Năng Chính
- 🔍 **Tìm Kiếm Chỗ Ở**:  
  Tìm kiếm nhanh dựa trên vị trí, mức giá, tiện ích (wifi, điều hòa, v.v.) và loại chỗ ở.
- 👤 **Quản Lý Người Dùng**:  
  Đăng ký, đăng nhập, xác thực qua token và quản lý thông tin cá nhân.
- 🏡 **Quản Lý Dữ Liệu Chỗ Ở**:  
  Thêm, sửa, xóa và xem chi tiết các danh sách chỗ ở với giao diện API thân thiện.
- 🌐 **API RESTful**:  
  Cung cấp các endpoint tiêu chuẩn để kết nối với frontend hoặc ứng dụng bên thứ ba.
- ⚡ **Hiệu Suất Cao**:  
  Tối ưu hóa truy vấn SQL để xử lý dữ liệu lớn một cách hiệu quả.

---

## 🛠 Công Nghệ Sử Dụng
- **Ngôn Ngữ**:  
  ![Python](https://img.shields.io/badge/Python-3.9+-blue)  
- **Framework**:  
  ![Django](https://img.shields.io/badge/Django-4.x-green)  
- **Cơ Sở Dữ Liệu**:  
  ![MySQL](https://img.shields.io/badge/MySQL-8.x-orange)  
- **Xác Thực**:  
  ![OAuth2](https://img.shields.io/badge/OAuth2-Security-yellow)
- **Công Cụ Hỗ Trợ**:    
  - 📦 `pip` - Quản lý gói phụ thuộc  
  - 🗄 `Django ORM` - Tương tác với cơ sở dữ liệu
  - 🔐 `django-oauth-toolkit` - Hỗ trợ OAuth2

---

## 📋 Yêu Cầu Hệ Thống
Để triển khai dự án, bạn cần chuẩn bị:
- 🖥 **Python**: Phiên bản 3.9 trở lên  
- 📦 **pip**: Công cụ quản lý gói của Python  
- 🗄 **MySQL**: Phiên bản 8.x trở lên  
- 🌐 **Git**: Để clone mã nguồn  

---

## ⚙ Hướng Dẫn Cài Đặt

### 1️⃣ Clone Repository
Tải mã nguồn về máy:
```bash
git clone https://github.com/HoDucLinh/Accommodation-search-system-BE.git
```
### 2️⃣ Di Chuyển Vào Thư Mục Dự Án
```bash
cd Accommodation-search-system-BE
```
### 3️⃣ Tạo Môi Trường Ảo
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate
```
### 4️⃣ Cài Đặt Các Gói Phụ Thuộc
```bash
pip install -r requirements.txt
```
### 5️⃣ Cấu Hình Cơ Sở Dữ Liệu
Đảm bảo MySQL đang chạy và đã tạo Database với tên accommodation_db.
Sau đó chạy lệnh dưới đây là thực hiện tạo bảng
```bash
python manage.py migrate
```
### 6️⃣ Khởi chạy ứng dụng
```bash
python manage.py runserver
```

📂 Cấu Trúc Thư Mục

Accommodation-search-system-BE/
├── 📁 accommodation_app/    # Ứng dụng chính của dự án
│   ├── 📁 migrations/       # 🗄 File migration cơ sở dữ liệu
│   ├── 📁 templates/        # 📄 Template HTML (nếu có)
│   ├── 📄 __init__.py       # 📜 File khởi tạo Python package
│   ├── 📄 admin.py          # 🖥 Định nghĩa giao diện admin
│   ├── 📄 apps.py           # ⚙ Cấu hình ứng dụng
│   ├── 📄 models.py         # 📋 Định nghĩa mô hình dữ liệu
│   ├── 📄 serializers.py    # 🔄 Chuyển đổi dữ liệu (cho API)
│   ├── 📄 tests.py          # 🧪 File kiểm thử
│   ├── 📄 urls.py           # 🛤️ Định nghĩa tuyến đường API
│   ├── 📄 views.py          # 🎮 Logic xử lý nghiệp vụ
├── 📁 accommodation_system/ # Thư mục chứa cấu hình dự án
│   ├── 📄 __init__.py       # 📜 File khởi tạo Python package
│   ├── 📄 asgi.py           # 🌐 Cấu hình ASGI (hỗ trợ async)
│   ├── 📄 settings.py       # ⚙ Cấu hình dự án (database, OAuth2, v.v.)
│   ├── 📄 urls.py           # 🛤️ Định nghĩa tuyến đường chính
│   ├── 📄 wsgi.py           # 🌐 Cấu hình WSGI (triển khai server)
├── 📄 .gitignore            # ❌ Danh sách file/thư mục bỏ qua
├── 📄 db.sqlite3            # 🗄 Cơ sở dữ liệu SQLite (dùng khi debug, không dùng MySQL)
├── 📄 manage.py             # 🛠 Công cụ quản lý Django
├── 📄 requirements.txt      # 📦 Danh sách dependencies
└── 📄 README.md             # 📖 File hướng dẫn này

📡 Danh Sách API
Dưới đây là các endpoint chính:

Phương Thức	          Endpoint	                Mô Tả
GET	          /api/accommodations/	            📋 Lấy danh sách tất cả chỗ ở
POST	        /api/accommodations/	            ➕ Thêm một chỗ ở mới
GET	          /api/accommodations/<id>/	        🔎 Xem chi tiết một chỗ ở
PUT	          /api/accommodations/<id>/	        ✏️ Cập nhật thông tin chỗ ở
DELETE	      /api/accommodations/<id>/	        🗑 Xóa một chỗ ở
POST	        /api/users/register/	            👤 Đăng ký người dùng mới
GET	          /o/authorize/	                    🔑 Yêu cầu xác thực OAuth2
POST	        /o/token/	                        🔐 Lấy access token OAuth2

📧 Liên Hệ
Nếu bạn có thắc mắc, ý tưởng hoặc muốn hợp tác:

- 👨‍💻 Tác Giả: Hồ Đức Linh
- 🌐 GitHub: HoDucLinh
- ✉️ Email: hoduclinh080204@gmail.com

### Ghi Chú:
-  ⚠ **Cảnh Báo**: 🚫 Mong quý người đọc không thực hiện push code mới vào nhánh main.
