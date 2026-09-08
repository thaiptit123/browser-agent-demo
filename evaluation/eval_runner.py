import asyncio
import os
import json
import pandas as pd
from datetime import datetime
from agent_builder import build_agent

async def run_evaluation():
    results = []
    target_url = "https://quotes.toscrape.com/"
    os.makedirs("evaluation/logs", exist_ok=True)
    
    # GROUND TRUTH CHO 10 BẢN GHI ĐẦU TIÊN
    ground_truth = [
        {"author": "Albert Einstein", "text_start": "The world as we have created it"},
        {"author": "J.K. Rowling", "text_start": "It is our choices, Harry"},
        {"author": "Albert Einstein", "text_start": "There are only two ways to live your life"},
        {"author": "Jane Austen", "text_start": "The person, be it gentleman or lady"},
        {"author": "Marilyn Monroe", "text_start": "Imperfection is beauty, madness is genius"},
        {"author": "Albert Einstein", "text_start": "Try not to become a man of success"},
        {"author": "André Gide", "text_start": "It is better to be hated for what you are"},
        {"author": "Thomas A. Edison", "text_start": "I have not failed. I've just found 10,000 ways"},
        {"author": "Eleanor Roosevelt", "text_start": "A woman is like a tea bag"},
        {"author": "Steve Martin", "text_start": "A day without sunshine is like, you know, night"}
    ]

    for i in range(1, 11):
        print(f"\n--- RUN {i}/10 ---")
        agent = build_agent(target_url)
        start_time = datetime.now()
        
        try:
            history = await agent.run(max_steps=8)
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            with open(f"evaluation/logs/run_{i}.json", "w", encoding="utf-8") as f:
                f.write(history.model_dump_json())
                
            structured_data = history.structured_output
            
            if structured_data and len(structured_data.quotes) == 10:
                # ĐỐI CHIẾU GROUND TRUTH TỪNG RECORD
                match_count = 0
                for j in range(10):
                    quote = structured_data.quotes[j]
                    if quote.author == ground_truth[j]["author"] and ground_truth[j]["text_start"] in quote.text:
                        match_count += 1
                
                if match_count == 10:
                    results.append({
                        "Run": i,
                        "Status": "Success",
                        "Records": 10,
                        "All_3_Fields_Present": True,
                        "Steps": len(history.history),
                        "Time_Seconds": round(duration, 1),
                        "Error": ""
                    })
                else:
                    results.append({
                        "Run": i,
                        "Status": "Failed",
                        "Records": 10,
                        "All_3_Fields_Present": True,
                        "Steps": len(history.history),
                        "Time_Seconds": round(duration, 1),
                        "Error": f"Ground truth mismatch (Matched {match_count}/10)"
                    })
            else:
                records = len(structured_data.quotes) if structured_data else 0
                results.append({
                    "Run": i,
                    "Status": "Failed",
                    "Records": records,
                    "All_3_Fields_Present": False,
                    "Steps": len(history.history),
                    "Time_Seconds": round(duration, 1),
                    "Error": "Not exactly 10 records"
                })
        except Exception as e:
            end_time = datetime.now()
            results.append({
                "Run": i,
                "Status": "Failed",
                "Records": 0,
                "All_3_Fields_Present": False,
                "Steps": 0,
                "Time_Seconds": round((end_time - start_time).total_seconds(), 1),
                "Error": str(e)
            })
            
    df = pd.DataFrame(results)
    df.to_csv("evaluation/evaluation_results.csv", index=False)
    print("\nEvaluation hoàn tất. Kết quả được lưu tại evaluation/evaluation_results.csv")

if __name__ == "__main__":
    asyncio.run(run_evaluation())
