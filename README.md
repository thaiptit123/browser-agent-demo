# Browser Agent Demo

Repository này chứa mã nguồn minh họa cách sử dụng thư viện `browser-use` kết hợp với model LLM cục bộ (Ollama) để điều khiển trình duyệt tự động trích xuất dữ liệu từ một trang web.

Đây là bài thực hành thuộc khóa học **AI Guru**, minh họa sức mạnh của việc dùng LLM đọc **Accessibility Tree** thay vì dùng các Selector CSS/XPath truyền thống vốn dễ vỡ.

## 📌 Các file trong Repository

- `scraper_agent.py`: Mã nguồn chính của Browser Agent.
- `result_quotes.csv`: File dữ liệu mẫu (10 câu nói) được Agent trích xuất thành công và xuất ra bằng Pandas.

## ⚙️ Yêu cầu hệ thống

Để chạy được mã nguồn này, bạn cần cài đặt:

1. **Python 3.11+**
2. Cài đặt các thư viện Python:
   ```bash
   pip install browser-use==0.13.8 playwright pandas pydantic
   playwright install
   ```
3. **Ollama**: Cài đặt [Ollama](https://ollama.com/) và tải model `qwen2.5:7b` (hoặc các model khác tùy cấu hình).
   ```bash
   ollama pull qwen2.5:7b
   ```

## 🚀 Cách chạy thử

Chạy trực tiếp file Python:
```bash
python scraper_agent.py
```

Agent sẽ tự động:
1. Mở một trình duyệt ẩn (headless).
2. Điều hướng đến `https://quotes.toscrape.com/`.
3. Nhìn và phân tích cấu trúc của trang web.
4. Trích xuất đúng 10 bản ghi đầu tiên với đầy đủ các trường `text`, `author`, `tags` theo chuẩn schema của Pydantic.
5. Lưu kết quả ra file `result_quotes.csv`.

## 🛡 Cân nhắc An toàn (Guardrails)
Mã nguồn này được thiết lập giới hạn vòng lặp tối đa `max_steps=20` để phòng trường hợp LLM bị "ảo giác" (hallucination) dẫn đến lặp vô hạn. Tuyệt đối tuân thủ `robots.txt` và không dùng script này để vượt qua các cơ chế Anti-Bot tự động.
