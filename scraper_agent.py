import asyncio
import pandas as pd
from typing import List
from pydantic import BaseModel, Field
from browser_use import Agent, ChatOllama

# 1. Định nghĩa cấu trúc dữ liệu đầu ra bằng Pydantic (Structured Output)
class Quote(BaseModel):
    text: str = Field(description="Nội dung câu nói")
    author: str = Field(description="Tên tác giả")
    tags: str = Field(description="Danh sách các thẻ (tags) tương ứng, nối nhau bằng dấu phẩy")

class QuotesData(BaseModel):
    quotes: List[Quote] = Field(description="Danh sách tối đa 10 câu nói đầu tiên tìm thấy trên trang")

async def main():
    # 2. Khởi tạo LLM. Sử dụng ChatOllama tích hợp sẵn của browser-use
    llm = ChatOllama(model="qwen2.5:7b", temperature=0.0)

    # 3. Khai báo Task chi tiết
    task_prompt = """
    1. Truy cập vào trang web: https://quotes.toscrape.com/
    2. Tìm danh sách các câu nói (quotes) đang được hiển thị trên trang này.
    3. Trích xuất thông tin của TỐI ĐA 10 câu nói đầu tiên.
    """

    # 4. Khởi tạo Agent với output_model_schema (Pydantic Model)
    print("🚀 Đang khởi tạo Browser Agent...")
    agent = Agent(
        task=task_prompt,
        llm=llm,
        output_model_schema=QuotesData
    )

    # 5. Thực thi Agent
    print("⏳ Agent bắt đầu duyệt web và suy luận. Vui lòng chờ (có thể mất 1-2 phút)...")
    history = await agent.run(max_steps=20)

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
        
        df_data = []
        for item in quotes_list:
            # item đang là Pydantic model Quote
            item_dict = item.model_dump()
            
            # Đề phòng LLM vẫn trả list dù đã yêu cầu chuỗi nối bằng dấu phẩy
            if isinstance(item_dict["tags"], list):
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
