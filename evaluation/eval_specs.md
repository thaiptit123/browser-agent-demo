# Evaluation Specifications (Môi trường thực nghiệm)

Kết quả đánh giá (Agent Evaluation) ghi nhận trong thư mục này được thực thi trên môi trường tiêu chuẩn sau:

- **Thiết bị:** Apple M2 (Silicon)
- **Bộ nhớ (RAM):** 16GB
- **Hệ điều hành:** macOS
- **Mô hình LLM:** `qwen2.5:7b` (chạy local qua Ollama)
- **Phiên bản Ollama:** `v0.3.0`
- **Phiên bản Thư viện:**
  - `browser-use==0.13.8`
  - `playwright==1.49.1` (hoặc tương đương)

Môi trường này đảm bảo độ trễ phản hồi của LLM ở mức trung bình khá (khoảng 30-40 token/s), ảnh hưởng trực tiếp đến thời gian hoàn thành (time_taken) được ghi nhận trong file `evaluation_results.csv`. Người tái lập thử nghiệm trên các cấu hình máy khác nhau có thể ghi nhận tốc độ nhanh hoặc chậm hơn.
