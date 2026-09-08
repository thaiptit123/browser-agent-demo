import asyncio
import pandas as pd
from agent_builder import build_agent, MAX_STEPS

async def main():
    print("🚀 Đang khởi tạo Browser Agent...")
    agent = build_agent("https://quotes.toscrape.com/")

    # 5. Thực thi Agent
    print("⏳ Agent bắt đầu duyệt web và suy luận. Vui lòng chờ (có thể mất 1-2 phút)...")
    history = await agent.run(max_steps=MAX_STEPS)

    # 6. Phân tích kết quả từ structured_output và xuất ra CSV
    print("✅ Agent đã hoàn thành tác vụ. Đang xử lý kết quả...")
    try:
        # Lấy output đã được Pydantic parse trực tiếp từ history (danh sách Quote)
        structured_data = history.structured_output
        
        if not structured_data:
            print("❌ Không tìm thấy structured_output. Có thể Agent thất bại.")
            return
            
        quotes_list = structured_data.quotes
        
        # Đảm bảo chỉ lấy 10 bản ghi và chuẩn hóa tags thành chuỗi cách bằng dấu phẩy
        quotes_list = quotes_list[:10]
        
        # [GUARDRAIL Kỹ thuật 2]: Output Content Filter (Lọc nội dung đầu ra)
        bad_words = ["ignore previous", "password", "hack", "system prompt"]
        
        df_data = []
        for item in quotes_list:
            # item đang là Pydantic model Quote
            item_dict = item.model_dump()
            
            # Output Content Filter check
            if any(bad_word in item_dict["text"].lower() for bad_word in bad_words):
                print(f"⚠️ Phát hiện nội dung đáng ngờ, loại bỏ record: {item_dict['text'][:30]}...")
                continue
            
            # tags đã được validate là list[str], giờ ta nối thành chuỗi
            item_dict["tags"] = ", ".join(item_dict["tags"])
                
            df_data.append(item_dict)
                
        # Dùng pandas xuất ra CSV
        df = pd.DataFrame(df_data)
        output_file = "result_quotes.csv"
        df.to_csv(output_file, index=False, encoding="utf-8-sig")
        
        print(f"🎉 Đã lưu thành công {len(df)} bản ghi vào file '{output_file}'!")
        print("\nMột vài dòng đầu của kết quả:")
        print(df.head(3))
        
    except Exception as e:
        print(f"❌ Có lỗi xảy ra trong quá trình xử lý: {e}")

if __name__ == "__main__":
    asyncio.run(main())
