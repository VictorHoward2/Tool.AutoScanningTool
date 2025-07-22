AutoScanningTool/
├── main.py                          ← Điểm khởi đầu
├── requirements.txt                 ← Danh sách thư viện
├── README.md                        ← Hướng dẫn sử dụng
├── config/
│   └── settings.py                  ← API key, path, cấu hình hệ thống, Danh sách từ khóa, có thể update sau
├── core/
│   ├── search_google.py             ← Tìm kiếm trên Google
│   ├── search_youtube.py           ← Tìm kiếm YouTube (sẽ thêm sau)
│   ├── translator.py               ← Dịch ngôn ngữ
│   ├── content_fetcher.py          ← Lấy nội dung web (Selenium, Requests)
│   ├── ai_processor.py             ← Tóm tắt, đánh giá liên quan, trích xuất thông tin
│   ├── exporter.py                 ← Xuất kết quả ra Excel
│   └── logger.py                   ← Xử lý ghi log
├── ui/
│   ├── app_ui.py                   ← Giao diện PySide6 (sau này)
│   └── components/                 ← Các component nhỏ cho GUI
│       └── result_table.py
├── data/
│   ├── output/                     ← Chứa file Excel xuất ra
│   └── logs/                       ← Chứa log file theo từng ngày
├── assets/                         ← Icon, hình ảnh, tài nguyên GUI
└── utils/
    ├── time_utils.py              ← Các hàm thời gian
    └── helpers.py                 ← Các hàm phụ trợ khác
