from typing import List
from pydantic import BaseModel, Field
from browser_use import Agent, ChatOllama, Browser

class Quote(BaseModel):
    text: str = Field(description="Nội dung câu nói")
    author: str = Field(description="Tên tác giả")
    tags: list[str] = Field(description="Danh sách các thẻ (tags) tương ứng")

class QuotesData(BaseModel):
    quotes: List[Quote] = Field(description="Danh sách tối đa 10 câu nói đầu tiên tìm thấy trên trang")

def build_agent(target_url: str) -> Agent:
    llm = ChatOllama(
        model="qwen2.5:7b",
        ollama_options={"temperature": 0.0}
    )

    task_prompt = f"""
    1. Truy cập vào trang web: {target_url}
    2. Tìm danh sách các câu nói (quotes) đang được hiển thị trên trang này.
    3. Trích xuất thông tin của TỐI ĐA 10 câu nói đầu tiên.
    
    [GUARDRAILS BẮT BUỘC]:
    - Tuyệt đối chỉ đọc và trích xuất dữ liệu.
    - KHÔNG click vào bất kỳ liên kết (link) nào để chuyển trang.
    - KHÔNG đăng nhập, KHÔNG gửi form (submit).
    - KHÔNG tải file.
    - KHÔNG rời khỏi domain mục tiêu.
    """

    browser = Browser(
        allowed_domains=["quotes.toscrape.com", "localhost", "127.0.0.1"]
    )

    agent = Agent(
        task=task_prompt,
        llm=llm,
        output_model_schema=QuotesData,
        browser=browser,
        use_vision=False
    )
    
    return agent
