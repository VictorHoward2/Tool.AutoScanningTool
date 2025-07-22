## 📁 Dự án AutoScanningTool - Cấu trúc thư mục

AutoScanningTool/
├── main.py ← 🎯 Điểm khởi đầu chạy tool
├── requirements.txt ← 📦 Danh sách thư viện cần cài
├── README.md ← 📖 Hướng dẫn sử dụng
│
├── config/
│ └── settings.py ← ⚙️ Cấu hình hệ thống (API key, path, từ khóa, có thể cập nhật sau)
│
├── core/ ← 🧠 Thành phần xử lý chính
│ ├── search_google.py ← 🔍 Tìm kiếm nội dung qua Google
│ ├── search_youtube.py ← 📺 Tìm kiếm YouTube (chức năng sẽ thêm sau)
│ ├── translator.py ← 🌐 Dịch đa ngôn ngữ
│ ├── content_fetcher.py ← 📄 Lấy nội dung từ web (dùng Selenium hoặc Requests)
│ ├── ai_processor.py ← 🤖 Xử lý AI: tóm tắt, phân tích, trích xuất
│ ├── exporter.py ← 📤 Xuất dữ liệu ra file Excel
│ └── logger.py ← 📝 Ghi log hoạt động của hệ thống
│
├── ui/ ← 🖥️ Giao diện người dùng (PySide6)
│ ├── assets/ ← 🎨 Icon, hình ảnh, tài nguyên cho GUI
│ ├── app_ui.py ← Giao diện chính
│ └── components/ ← 📦 Các thành phần con của GUI
│ └── result_table.py ← 📊 Bảng hiển thị kết quả
│
├── data/ ← 💾 Dữ liệu sinh ra trong quá trình chạy
│ ├── output/ ← 📁 Chứa các file Excel kết quả
│ └── logs/ ← 📁 Chứa log theo ngày
│
├── utils/ ← 🧰 Các hàm tiện ích
│ ├── time_utils.py ← ⏰ Xử lý thời gian, định dạng
│ └──helpers.py ← 🧪 Các hàm phụ trợ dùng chung
│
└──────────────────────