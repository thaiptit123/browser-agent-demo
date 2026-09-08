import asyncio
import time
import os
import sys
import pandas as pd
from pydantic import BaseModel, Field
from typing import List

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from agent_builder import build_agent

async def run_evaluation():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    logs_dir = os.path.join(current_dir, "logs")
    os.makedirs(logs_dir, exist_ok=True)
    
    results = []
    
    for i in range(1, 11):
        print(f"--- Running iteration {i}/10 ---")
        start_time = time.time()
        agent = build_agent("https://quotes.toscrape.com/")
        
        try:
            history = await agent.run(max_steps=20)
            elapsed = round(time.time() - start_time, 1)
            steps_taken = len(history.history)
            
            # Save raw log
            log_file = os.path.join(logs_dir, f"run_{i}.json")
            with open(log_file, "w", encoding="utf-8") as f:
                f.write(history.model_dump_json())
            
            structured_data = history.structured_output
            if structured_data and len(structured_data.quotes) == 10:
                results.append({
                    "run_id": i,
                    "result": "Success",
                    "records_extracted": 10,
                    "all_fields_present": True,
                    "steps": steps_taken,
                    "time_seconds": elapsed,
                    "error": "",
                    "model": "qwen2.5:7b"
                })
            else:
                extracted = len(structured_data.quotes) if structured_data else 0
                raise ValueError(f"Extracted only {extracted} records")
        except Exception as e:
            print(f"Run {i} failed: {e}")
            elapsed = round(time.time() - start_time, 1)
            # steps_taken depends on if history was created, fallback to 0 if not
            steps_taken = len(history.history) if 'history' in locals() and history else 0
            results.append({
                "run_id": i,
                "result": "Failed",
                "records_extracted": 0,
                "all_fields_present": False,
                "steps": steps_taken,
                "time_seconds": elapsed,
                "error": str(e),
                "model": "qwen2.5:7b"
            })
            
    df = pd.DataFrame(results)
    output_path = os.path.join(current_dir, "evaluation_results.csv")
    df.to_csv(output_path, index=False)
    print(f"Evaluation complete. Results saved to {output_path}")

if __name__ == "__main__":
    asyncio.run(run_evaluation())
