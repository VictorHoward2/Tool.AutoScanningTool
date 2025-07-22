# 🤖 AutoScanningTool

**AutoScanningTool** là một công cụ tự động hóa quy trình tìm kiếm thông tin trên internet, trích xuất nội dung, xử lý bằng AI (tóm tắt, phân tích), dịch thuật và xuất ra file Excel. Công cụ có giao diện người dùng (GUI) thân thiện được xây dựng bằng PySide6.

---

## 📁 Cấu trúc thư mục

```bash
AutoScanningTool/
├── main.py                # 🎯 Điểm khởi đầu chạy tool
├── requirements.txt       # 📦 Danh sách thư viện cần cài
├── README.md              # 📖 Hướng dẫn sử dụng

├── config/                # ⚙️ Cấu hình hệ thống
│   └── settings.py        #    API key, path, từ khóa, có thể cập nhật sau

├── core/                  # 🧠 Thành phần xử lý chính
│   ├── search_google.py   # 🔍 Tìm kiếm nội dung qua Google
│   ├── search_youtube.py  # 📺 Tìm kiếm YouTube (chức năng sẽ thêm sau)
│   ├── translator.py      # 🌐 Dịch đa ngôn ngữ
│   ├── content_fetcher.py # 📄 Lấy nội dung từ web (dùng Selenium hoặc Requests)
│   ├── ai_processor.py    # 🤖 Xử lý AI: tóm tắt, phân tích, trích xuất
│   ├── exporter.py        # 📤 Xuất dữ liệu ra file Excel
│   └── logger.py          # 📝 Ghi log hoạt động của hệ thống

├── ui/                    # 🖥️ Giao diện người dùng (PySide6)
│   ├── assets/            # 🎨 Icon, hình ảnh, tài nguyên cho GUI
│   ├── app_ui.py          #    Giao diện chính
│   └── components/        # 📦 Các thành phần con của GUI
│       └── result_table.py # 📊 Bảng hiển thị kết quả

├── data/                  # 💾 Dữ liệu sinh ra trong quá trình chạy
│   ├── output/            # 📁 Chứa các file Excel kết quả
│   └── logs/              # 📁 Chứa log theo ngày

├── utils/                 # 🧰 Các hàm tiện ích
│   ├── time_utils.py      # ⏰ Xử lý thời gian, định dạng
│   └── helpers.py         # 🧪 Các hàm phụ trợ dùng chung
```

---

## 🚀 Cách sử dụng
1. Cài đặt các thư viện cần thiết:
    ```bash
    pip install -r requirements.txt
    ```
2. Chạy tool:
    ```bash
    python main.py
    ```

## 📌 Ghi chú
- Đảm bảo đã cấu hình file `settings.py` trước khi chạy tool.
