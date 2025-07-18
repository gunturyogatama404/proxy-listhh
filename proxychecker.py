import requests
import threading
from queue import Queue
from random import choice

INPUT_FILE = "proxies.txt"
OUTPUT_FILE = "result.txt"
USER_AGENT_FILE = "user_agents.txt"
API_URL = "https://api.bringyour.com/my-ip-info"
THREADS = 500
TIMEOUT = 10

proxy_queue = Queue()
lock = threading.Lock()

# Load proxy list, hapus duplikat
def load_proxies():
    with open(INPUT_FILE, "r") as f:
        return list(set([line.strip() for line in f if line.strip()]))

# Load user agents dari file
def load_user_agents():
    with open(USER_AGENT_FILE, "r") as f:
        return [ua.strip() for ua in f if ua.strip()]

# Cek 1 proxy
def check_proxy(proxy, user_agents):
    try:
        headers = {"User-Agent": choice(user_agents)}
        proxies = {"http": proxy, "https": proxy}
        response = requests.get(API_URL, headers=headers, proxies=proxies, timeout=TIMEOUT)

        if response.status_code == 200 and "ip" in response.text:
            data = response.json()
            result = (
                f"[✓] {proxy} | IP: {data.get('ip')} | Country: {data.get('country')} | "
                f"VPN: {data.get('vpn')} | Proxy: {data.get('proxy')} | TOR: {data.get('tor')} | "
                f"Relay: {data.get('relay')} | Hosting: {data.get('hosting')} | Service: {data.get('service', '')}"
            )
            with lock:
                print(result)
                with open(OUTPUT_FILE, "a") as out:
                    out.write(result + "\n")
    except Exception:
        pass

# Worker thread
def worker(user_agents):
    while not proxy_queue.empty():
        proxy = proxy_queue.get()
        check_proxy(proxy, user_agents)
        proxy_queue.task_done()

# Main function
def main():
    proxies = load_proxies()
    user_agents = load_user_agents()

    print(f"🔍 Checking {len(proxies)} proxies...")

    open(OUTPUT_FILE, "w").close()  # clear result file

    for proxy in proxies:
        proxy_queue.put(proxy)

    threads = []
    for _ in range(min(THREADS, len(proxies))):
        t = threading.Thread(target=worker, args=(user_agents,))
        t.start()
        threads.append(t)

    for t in threads:
        t.join()

    print("✅ Done!")

if __name__ == "__main__":
    main()
