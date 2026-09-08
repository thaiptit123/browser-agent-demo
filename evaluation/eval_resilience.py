import asyncio
import os
import pandas as pd
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
    results_data = []
    
    for case in test_cases:
        print(f"\n[Test Case]: {case['name']}")
        task_prompt = f"Mở trang web {case['url']} và trích xuất danh sách tất cả các câu nói (quotes) hiện có."
        
        agent = Agent(task=task_prompt, llm=llm, output_model_schema=QuotesData)
        try:
            history = await agent.run(max_steps=10)
            structured_data = history.structured_output
            
            if structured_data and len(structured_data.quotes) == 10:
                print("✅ Thành công! Trích xuất đủ 10/10 records.")
                results_data.append({
                    "case": case["name"],
                    "result": "Success",
                    "records_extracted": 10
                })
            else:
                actual = len(structured_data.quotes) if structured_data else 0
                print(f"❌ Thất bại: Chỉ trích xuất {actual}/10 records.")
                results_data.append({
                    "case": case["name"],
                    "result": "Failed",
                    "records_extracted": actual
                })
        except Exception as e:
            print(f"❌ Lỗi thực thi: {e}")
            results_data.append({
                "case": case["name"],
                "result": "Error",
                "records_extracted": 0
            })
            
    # Xuất kết quả ra CSV
    df = pd.DataFrame(results_data)
    csv_path = os.path.join(current_dir, "resilience_results.csv")
    df.to_csv(csv_path, index=False)
    print(f"\n Đã lưu báo cáo vào {csv_path}")

if __name__ == "__main__":
    asyncio.run(run_resilience_test())
