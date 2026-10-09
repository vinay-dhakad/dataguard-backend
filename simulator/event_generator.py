import argparse, json, time, requests

URL = "http://127.0.0.1:8000/api/events"

SCENARIOS = {
    "unauthorized_download": {"user_id": 1, "file_id": 3, "action": "DOWNLOAD", "destination": "LOCAL_DEVICE"},
    "usb_exfiltration": {"user_id": 3, "file_id": 5, "action": "USB_COPY", "destination": "USB"},
    "personal_cloud": {"user_id": 1, "file_id": 3, "action": "UPLOAD", "destination": "PERSONAL_CLOUD"},
    "personal_email": {"user_id": 1, "file_id": 3, "action": "EMAIL_ATTACHMENT", "destination": "PERSONAL_EMAIL"},
}

def send(event):
    r = requests.post(URL, json=event, timeout=10)
    print(r.status_code)
    print(json.dumps(r.json(), indent=2))

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--scenario", choices=list(SCENARIOS) + ["all"], default="all")
    p.add_argument("--count", type=int, default=1)
    a = p.parse_args()
    items = SCENARIOS.items() if a.scenario == "all" else [(a.scenario, SCENARIOS[a.scenario])]
    for name, event in items:
        print(f"--- {name} ---")
        for _ in range(a.count):
            send(event)
            time.sleep(1)

if __name__ == "__main__":
    main()
