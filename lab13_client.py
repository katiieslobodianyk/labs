import requests
import sys

BASE_URL = "http://localhost:8000"

def call_fetch(url, regex=None):
    resp = requests.post(f"{BASE_URL}/fetch", json={"url": url, "regex": regex})
    return resp.json()

def call_bw_image(url, output_path="output_gray.jpg"):
    resp = requests.post(f"{BASE_URL}/bw-image", json={"url": url})
    with open(output_path, "wb") as f:
        f.write(resp.content)
    print(f"Grayscale image saved as {output_path}")

def call_top(limit=20):
    resp = requests.get(f"{BASE_URL}/stats/top", params={"limit": limit})
    return resp.json()

def call_agents():
    resp = requests.get(f"{BASE_URL}/stats/agents")
    return resp.json()

def call_hourly(hour=None):
    params = {"hour": hour} if hour else {}
    resp = requests.get(f"{BASE_URL}/stats/hourly", params=params)
    return resp.json()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage:")
        print("  client.py fetch <url> [regex]")
        print("  client.py bw <url>")
        print("  client.py top [limit]")
        print("  client.py agents")
        print("  client.py hourly [YYYYMMDDHH]")
        sys.exit(1)
    cmd = sys.argv[1]
    if cmd == "fetch":
        url = sys.argv[2]
        regex = sys.argv[3] if len(sys.argv) > 3 else None
        result = call_fetch(url, regex)
        print("Headers:", result["headers"])
        print("Matched lines:", result["matched_lines"])
    elif cmd == "bw":
        url = sys.argv[2]
        call_bw_image(url)
    elif cmd == "top":
        limit = int(sys.argv[2]) if len(sys.argv) > 2 else 20
        data = call_top(limit)
        for row in data:
            print(f"{row['title']}: {row['views']} views")
    elif cmd == "agents":
        data = call_agents()
        for row in data:
            print(f"{row['agent']}: {row['views']} views")
    elif cmd == "hourly":
        hour = sys.argv[2] if len(sys.argv) > 2 else None
        data = call_hourly(hour)
        for row in data:
            print(f"{row['hour']}: {row['views']} views")
    else:
        print("Unknown command")
