import json
import os
import time
import urllib.request
import urllib.error
from concurrent.futures import ThreadPoolExecutor, as_completed

LOGIN_URL = "http://127.0.0.1:5001/login"

TOTAL_REQUESTS = 5000
CONCURRENT_CLIENTS = 20

login_data = json.dumps({
    "username": os.environ["AUTH_USERNAME"],
    "password": os.environ["AUTH_PASSWORD"]
}).encode("utf-8")


def send_login():
    login_request = urllib.request.Request(
        LOGIN_URL,
        data=login_data,
        headers={"Content-Type": "application/json"},
        method="POST"
    )

    try:
        with urllib.request.urlopen(login_request, timeout=10) as response:
            data = json.load(response)
            return response.status == 200 and "token" in data
    except (urllib.error.URLError, TimeoutError, ValueError):
        return False


successful = 0
failed = 0

print(f"Starting Authentication load test: {TOTAL_REQUESTS} requests")
print(f"Concurrent clients: {CONCURRENT_CLIENTS}")

start = time.perf_counter()

with ThreadPoolExecutor(max_workers=CONCURRENT_CLIENTS) as executor:
    futures = [
        executor.submit(send_login)
        for _ in range(TOTAL_REQUESTS)
    ]

    for future in as_completed(futures):
        if future.result():
            successful += 1
        else:
            failed += 1

elapsed = time.perf_counter() - start
throughput = TOTAL_REQUESTS / elapsed

print("\n--- Authentication Load Test Results ---")
print(f"Total requests: {TOTAL_REQUESTS}")
print(f"Concurrent clients: {CONCURRENT_CLIENTS}")
print(f"Successful: {successful}")
print(f"Failed: {failed}")
print(f"Duration: {elapsed:.2f} seconds")
print(f"Throughput: {throughput:.2f} requests/second")
