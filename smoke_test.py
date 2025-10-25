import httpx
import sys
import time

def smoke_test(url, keyword, retries=5, delay=2):
    for attempt in range(retries):
        try:
            response = httpx.get(url)
        except Exception as e:
            print(f"Attempt {attempt+1}: Exception occurred - {e}")
            time.sleep(delay)
            continue

        if response.status_code == 200 and keyword in response.text:
            print("✅ Smoke test passed: Keyword found in response.")
            sys.exit(0)
        else:
            print(f"Attempt {attempt+1}: Keyword not found or bad response.")
            time.sleep(delay)

    print("❌ Smoke test failed after retries.")
    sys.exit(1)

# Run the smoke test
smoke_test("http://localhost:8000", "DevOps Dashboard")
