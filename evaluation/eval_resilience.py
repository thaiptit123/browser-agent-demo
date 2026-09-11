import asyncio
import os
import sys
import threading
import http.server
import socketserver
import pandas as pd
import time
from datetime import datetime

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from agent_builder import build_agent, MAX_STEPS

def start_server(directory, port):
    class Handler(http.server.SimpleHTTPRequestHandler):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, directory=directory, **kwargs)
        def log_message(self, format, *args):
            pass # Disable logging

    httpd = socketserver.TCPServer(("", port), Handler)
    thread = threading.Thread(target=httpd.serve_forever)
    thread.daemon = True
    thread.start()
    return httpd

async def run_resilience_test():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    fixtures_dir = os.path.join(current_dir, 'fixtures')
    
    # Khởi tạo HTTP server phục vụ thư mục fixtures
    port = 8000
    print(f"Khởi động HTTP server tại http://localhost:{port}/")
    httpd = start_server(fixtures_dir, port)
    
    # Đợi server khởi động
    time.sleep(1)
    
    before_url = f"http://localhost:{port}/quotes_before.html"
    after_url = f"http://localhost:{port}/quotes_after.html"
    
    test_cases = [
        {"name": "Before (class='.quote')", "url": before_url},
        {"name": "After (class='.item' + dummy div)", "url": after_url}
    ]
    
    # Ground truth từ trang web (10 quotes đầu tiên)
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
    
    print("=== BẮT ĐẦU RESILIENCE TEST (10 LƯỢT/BẢN) ===")
    results_data = []
    
    for case in test_cases:
        print(f"\n[Test Case]: {case['name']}")
        for run_idx in range(1, 11):
            print(f"  -> Lượt {run_idx}/10...")
            agent = build_agent(case['url'])
            start_time = datetime.now()
            
            try:
                history = await agent.run(max_steps=MAX_STEPS)
                end_time = datetime.now()
                duration = (end_time - start_time).total_seconds()
                steps = len(history.history)
                structured_data = history.structured_output
                
                records_extracted = len(structured_data.quotes) if structured_data else 0
                match_count = 0
                
                if structured_data and records_extracted == 10:
                    for j in range(10):
                        quote = structured_data.quotes[j]
                        if quote.author == ground_truth[j]["author"] and ground_truth[j]["text_start"] in quote.text:
                            match_count += 1
                elif structured_data and records_extracted > 0 and records_extracted < 10:
                    # Partial match logic (just for rough metric)
                    for j in range(min(records_extracted, 10)):
                        quote = structured_data.quotes[j]
                        # find if this quote matches ANY in ground truth
                        for gt in ground_truth:
                            if quote.author == gt["author"] and gt["text_start"] in quote.text:
                                match_count += 1
                                break
                
                is_success = (match_count == 10)
                if is_success:
                    result_str = "Success"
                    print(f"    ✅ Thành công! (Steps: {steps}, Time: {duration:.1f}s)")
                else:
                    result_str = "Failed"
                    print(f"    ❌ Thất bại: Trích xuất {records_extracted}/10, Khớp {match_count}/10. (Steps: {steps}, Time: {duration:.1f}s)")
                
                results_data.append({
                    "case": case["name"],
                    "run": run_idx,
                    "result": result_str,
                    "records_extracted": records_extracted,
                    "matched_gt": match_count,
                    "steps": steps,
                    "time_seconds": round(duration, 1)
                })
                
            except Exception as e:
                end_time = datetime.now()
                duration = (end_time - start_time).total_seconds()
                print(f"    ❌ Lỗi thực thi: {e}")
                results_data.append({
                    "case": case["name"],
                    "run": run_idx,
                    "result": "Error",
                    "records_extracted": 0,
                    "matched_gt": 0,
                    "steps": 0,
                    "time_seconds": round(duration, 1)
                })
            
            # Short sleep between runs
            time.sleep(2)
            
    # Xuất kết quả chi tiết ra CSV
    df = pd.DataFrame(results_data)
    csv_raw_path = os.path.join(current_dir, "resilience_results_raw.csv")
    df.to_csv(csv_raw_path, index=False)
    print(f"\n Đã lưu báo cáo chi tiết vào {csv_raw_path}")
    
    # Tính toán bảng tóm tắt
    summary_data = []
    for case in test_cases:
        case_df = df[df["case"] == case["name"]]
        success_rate = (len(case_df[case_df["result"] == "Success"]) / len(case_df)) * 100
        mean_extracted = case_df["records_extracted"].mean()
        std_extracted = case_df["records_extracted"].std()
        mean_matched = case_df["matched_gt"].mean()
        mean_time = case_df["time_seconds"].mean()
        
        summary_data.append({
            "case": case["name"],
            "success_rate_percent": round(success_rate, 1),
            "mean_extracted": round(mean_extracted, 1),
            "std_extracted": round(std_extracted, 2),
            "mean_matched": round(mean_matched, 1),
            "mean_time_seconds": round(mean_time, 1)
        })
        
    df_summary = pd.DataFrame(summary_data)
    csv_summary_path = os.path.join(current_dir, "resilience_results_summary.csv")
    df_summary.to_csv(csv_summary_path, index=False)
    print(f" Đã lưu báo cáo tóm tắt vào {csv_summary_path}")
    
    # In báo cáo tóm tắt ra console
    print("\n=== BẢNG TÓM TẮT RESILIENCE ===")
    print(df_summary.to_string(index=False))
    
    # Ghi đè lại resilience_results.csv (backward compatibility for markdown/pdf referencing)
    df_summary.to_csv(os.path.join(current_dir, "resilience_results.csv"), index=False)
    
    # Tắt HTTP server
    httpd.shutdown()

if __name__ == "__main__":
    asyncio.run(run_resilience_test())
