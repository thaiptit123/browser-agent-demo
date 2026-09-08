import asyncio
import os
import sys
import threading
import http.server
import socketserver
import pandas as pd
import time

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
    
    print("=== BẮT ĐẦU RESILIENCE TEST ===")
    results_data = []
    
    for case in test_cases:
        print(f"\n[Test Case]: {case['name']}")
        
        agent = build_agent(case['url'])
        try:
            history = await agent.run(max_steps=MAX_STEPS)
            structured_data = history.structured_output
            
            if structured_data and len(structured_data.quotes) == 10:
                match_count = 0
                for j in range(10):
                    quote = structured_data.quotes[j]
                    if quote.author == ground_truth[j]["author"] and ground_truth[j]["text_start"] in quote.text:
                        match_count += 1
                
                if match_count == 10:
                    print("✅ Thành công! Trích xuất đủ và đúng 10/10 records.")
                    results_data.append({
                        "case": case["name"],
                        "result": "Success",
                        "records_extracted": 10
                    })
                else:
                    print(f"❌ Thất bại: Trích xuất 10 records nhưng sai Ground Truth (Matched {match_count}/10).")
                    results_data.append({
                        "case": case["name"],
                        "result": f"Failed (GT mismatch {match_count}/10)",
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
    
    # Tắt HTTP server
    httpd.shutdown()

if __name__ == "__main__":
    asyncio.run(run_resilience_test())
