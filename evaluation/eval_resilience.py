import asyncio
import os
from pydantic import BaseModel, Field
from typing import List
from browser_use import Agent, ChatOllama

class Quote(BaseModel):
    text: str
    author: str
    tags: list[str]

class QuotesData(BaseModel):
    quotes: List[Quote]

async def run_resilience_test():
    llm = ChatOllama(model="qwen2.5:7b", ollama_options={"temperature": 0.0})
    
    # Lấy đường dẫn tuyệt đối của thư mục fixtures
    current_dir = os.path.dirname(os.path.abspath(__file__))
    before_url = f"file://{os.path.join(current_dir, 'fixtures', 'quotes_before.html')}"
    after_url = f"file://{os.path.join(current_dir, 'fixtures', 'quotes_after.html')}"
    
    test_cases = [
        {"name": "Before (class='.quote')", "url": before_url},
        {"name": "After (class='.item' + dummy div)", "url": after_url}
    ]
    
    print("=== BẮT ĐẦU RESILIENCE TEST ===")
    
    for case in test_cases:
        print(f"\n[Test Case]: {case['name']}")
        task_prompt = f"Mở trang web {case['url']} và trích xuất danh sách tất cả các câu nói (quotes) hiện có."
        
        agent = Agent(task=task_prompt, llm=llm, output_model_schema=QuotesData)
        try:
            history = await agent.run(max_steps=10)
            structured_data = history.structured_output
            
            if structured_data and len(structured_data.quotes) > 0:
                print(f"✅ Thành công! Trích xuất được {len(structured_data.quotes)} records.")
            else:
                print("❌ Thất bại: Không tìm thấy dữ liệu.")
        except Exception as e:
            print(f"❌ Lỗi thực thi: {e}")

if __name__ == "__main__":
    asyncio.run(run_resilience_test())
