import asyncio
import time
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

async def run_evaluation():
    llm = ChatOllama(model="qwen2.5:7b", ollama_options={"temperature": 0.0})
    task_prompt = "Trích xuất 10 câu nói đầu tiên từ https://quotes.toscrape.com/"
    
    results = []
    
    for i in range(1, 11):
        print(f"--- Running iteration {i}/10 ---")
        start_time = time.time()
        agent = Agent(task=task_prompt, llm=llm, output_model_schema=QuotesData)
        
        try:
            history = await agent.run(max_steps=20)
            elapsed = round(time.time() - start_time, 1)
            
            structured_data = history.structured_output
            if structured_data and len(structured_data.quotes) > 0:
                results.append({
                    "run_id": i,
                    "result": "Success",
                    "records_extracted": len(structured_data.quotes),
                    "all_fields_present": True,
                    "steps": len(history.history),
                    "time_seconds": elapsed,
                    "model": "qwen2.5:7b"
                })
            else:
                raise ValueError("No data extracted")
        except Exception as e:
            print(f"Run {i} failed: {e}")
            results.append({
                "run_id": i,
                "result": "Failed",
                "records_extracted": 0,
                "all_fields_present": False,
                "steps": 0,
                "time_seconds": 0,
                "model": "qwen2.5:7b"
            })
            
    df = pd.DataFrame(results)
    df.to_csv("evaluation_results.csv", index=False)
    print("Evaluation complete. Results saved to evaluation_results.csv")

if __name__ == "__main__":
    asyncio.run(run_evaluation())
