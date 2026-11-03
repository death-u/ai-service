"""
End-to-end check against a RUNNING service (local or deployed).

Usage:
    python scripts/smoke_test.py http://127.0.0.1:8000 YOUR_SERVICE_API_KEY

Uses only the Python standard library.
"""
import json
import sys
import urllib.error
import urllib.request

PAYLOAD = {
    "productId": "product_001",
    "retailerId": "retailer_001",
    "forecastDays": 7,
    "historicalSales": [
        {"date": "2026-10-25", "quantity": 15},
        {"date": "2026-10-26", "quantity": 18},
    ],
}


def call(method, url, body=None, key=None):
    headers = {"Content-Type": "application/json"}
    if key:
        headers["X-API-Key"] = key
    data = json.dumps(body).encode() if body is not None else None
    request = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(request, timeout=15) as response:
            return response.status, json.loads(response.read())
    except urllib.error.HTTPError as error:
        return error.code, json.loads(error.read() or b"{}")


def check(name, condition, detail=""):
    print(f"[{'PASS' if condition else 'FAIL'}] {name} {detail}")
    return condition


def main():
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    base, key = sys.argv[1].rstrip("/"), sys.argv[2]
    results = []

    status, body = call("GET", f"{base}/api/v1/health")
    results.append(check("health returns 200", status == 200 and body.get("success"), f"(status {status})"))

    status, _ = call("POST", f"{base}/api/v1/predict-demand", PAYLOAD)
    results.append(check("predict without key is rejected (401)", status == 401, f"(status {status})"))

    status, _ = call("POST", f"{base}/api/v1/predict-demand", PAYLOAD, key="wrong-key")
    results.append(check("predict with wrong key is rejected (401)", status == 401, f"(status {status})"))

    status, body = call("POST", f"{base}/api/v1/predict-demand", PAYLOAD, key)
    ok = status == 200 and body.get("data", {}).get("predictedDemand") == 116
    results.append(check("predict with valid key returns 116 for the document example", ok, f"(status {status})"))
    if status == 200:
        print(json.dumps(body, indent=2))

    bad = dict(PAYLOAD, forecastDays=0)
    status, body = call("POST", f"{base}/api/v1/predict-demand", bad, key)
    results.append(check("invalid payload returns 400 with errors", status == 400 and body.get("errors"), f"(status {status})"))

    print("\nALL CHECKS PASSED" if all(results) else "\nSOME CHECKS FAILED")
    sys.exit(0 if all(results) else 1)


if __name__ == "__main__":
    main()
