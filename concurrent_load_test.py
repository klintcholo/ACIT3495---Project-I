import json
import os
import time
import urllib.request
import urllib.error
from concurrent.futures import ThreadPoolExecutor, as_completed

LOGIN_URL = "http://127.0.0.1:5001/login"
GRADES_URL = "http://127.0.0.1:5000/grades"

TOTAL_REQUESTS = 500
CONCURRENT_CLIENTS = 10

# Get a fresh JWT token
login_data = json.dumps({
    "username": os.environ["AUTH_USERNAME"],
    "password": os.environ["AUTH_PASSWORD"]
}).encode("utf-8")

login_request = urllib.request.Request(
    LOGIN_URL,
    data=login_data,
    headers={"Content-Type": "application/json"},
    method="POST"
)

with urllib.request.urlopen(login_request, timeout=5) as response:
    token = json.load(response)["token"]


# Each worker sends one grade request
def send_grade(i):
    grade_data = json.dumps({
        "student_id": f"CONCURRENT{i:04d}",
        "course": "ACIT3495",
        "grade": 85
    }).encode("utf-8")

    grade_request = urllib.request.Request(
        GRADES_URL,
        data=grade_data,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}"
        },
        method="POST"
    )

    try:
        with urllib.request.urlopen(grade_request, timeout=10) as response:
            return response.status == 201
    except (urllib.error.URLError, TimeoutError):
        return False


successful = 0
failed = 0

print(f"Starting concurrent load test: {TOTAL_REQUESTS} requests")
print(f"Concurrent clients: {CONCURRENT_CLIENTS}")

start = time.perf_counter()

# Run requests concurrently
with ThreadPoolExecutor(max_workers=CONCURRENT_CLIENTS) as executor:
    futures = [
        executor.submit(send_grade, i)
        for i in range(TOTAL_REQUESTS)
    ]

    for future in as_completed(futures):
        if future.result():
            successful += 1
        else:
            failed += 1

elapsed = time.perf_counter() - start
throughput = TOTAL_REQUESTS / elapsed

print("\n--- Concurrent Load Test Results ---")
print(f"Total requests: {TOTAL_REQUESTS}")
print(f"Concurrent clients: {CONCURRENT_CLIENTS}")
print(f"Successful: {successful}")
print(f"Failed: {failed}")
print(f"Duration: {elapsed:.2f} seconds")
print(f"Throughput: {throughput:.2f} requests/second")
