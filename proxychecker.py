import requests
import concurrent.futures
import json
import random

# === KONFIGURASI ===
INPUT_FILE = "proxies.txt"
USERAGENT_FILE = "user_agent.txt"
OUTPUT_FILE = "working_detailed.txt"
TARGET_URL = "https://api.bringyour.com/my-ip-info"
MAX_THREADS = 100
TIMEOUT = 10

# === BACA USER-AGENT DARI FILE ===
try:
    with open(USERAGENT_FILE, "r") as f:
        USER_AGENTS = [ua.strip() for ua in f if ua.strip()]
    if not USER_AGENTS:
        raise ValueError("File useragent.txt kosong!")
except Exception as e:
    print(f"Gagal membaca '{USERAGENT_FILE}': {e}")
    USER_AGENTS = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)",
        "Mozilla/5.0 (X11; Linux x86_64)",
        "Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X)",
        "Mozilla/5.0 (Linux; Android 11; SM-G991B)",
        "Mozilla/5.0 (iPad; CPU OS 14_2 like Mac OS X)",
        "Mozilla/5.0 (Windows NT 6.1; Win64; x64)",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6)",
    ]
    print("Menggunakan default User-Agent.")

def get_random_headers():
    return {
        "User-Agent": random.choice(USER_AGENTS)
    }

def detect_proxy_type(proxy_raw):
    proxy_raw = proxy_raw.strip()
    if proxy_raw.startswith("http://") or proxy_raw.startswith("socks5://"):
        return proxy_raw
    return "http://" + proxy_raw

def parse_response(response_json):
    info = response_json.get("info", {})
    location = info.get("location", {})
    privacy = info.get("privacy", {})
    country = location.get("country", {}).get("name", "Unknown")

    return {
        "ip": info.get("ip", "N/A"),
        "country": country,
        "vpn": privacy.get("vpn", False),
        "proxy": privacy.get("proxy", False),
        "tor": privacy.get("tor", False),
        "relay": privacy.get("relay", False),
        "hosting": privacy.get("hosting", False),
        "service": privacy.get("service", "")
    }

def check(proxy):
    proxy_fmt = detect_proxy_type(proxy)
    proxies = {
        "http": proxy_fmt,
        "https": proxy_fmt
    }

    try:
        r = requests.get(TARGET_URL, headers=get_random_headers(), proxies=proxies, timeout=TIMEOUT)
        if r.status_code == 200:
            data = parse_response(r.json())

            log_line = (
                f"[✓] {proxy_fmt} | "
                f"IP: {data['ip']} | "
                f"Country: {data['country']} | "
                f"VPN: {data['vpn']} | "
                f"Proxy: {data['proxy']} | "
                f"TOR: {data['tor']} | "
                f"Relay: {data['relay']} | "
                f"Hosting: {data['hosting']} | "
                f"Service: {data['service']}"
            )

            print(log_line)
            with open(OUTPUT_FILE, "a") as f:
                f.write(log_line + "\n")

    except Exception as e:
        print(f"[✗] {proxy_fmt} -> {type(e).__name__}")

def main():
    try:
        with open(INPUT_FILE, "r") as f:
            proxy_list = [p.strip() for p in f if p.strip()]
    except FileNotFoundError:
        print(f"File '{INPUT_FILE}' tidak ditemukan.")
        return

    with open(OUTPUT_FILE, "w") as f:
        f.write("=== WORKING PROXY DETAIL LOG ===\n")

    with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_THREADS) as executor:
        executor.map(check, proxy_list)

    print("\n✅ DONE! Hasil detail disimpan di:", OUTPUT_FILE)

if __name__ == "__main__":
    main()
