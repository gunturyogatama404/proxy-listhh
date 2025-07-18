import threading
import random
import subprocess
import time
import json

proxy_file = "proxies.txt"
user_agent_file = "user_agents.txt"
output_file = "result.txt"
MAX_THREADS = 200  # jumlah thread paralel maksimal

lock = threading.Lock()
sema = threading.Semaphore(MAX_THREADS)
printed = set()

# Load user agents
with open(user_agent_file, "r") as f:
    user_agents = [line.strip() for line in f if line.strip()]

# Load proxies
with open(proxy_file, "r") as f:
    proxies = list(set([line.strip() for line in f if line.strip()]))

def check_proxy(proxy):
    with sema:
        user_agent = random.choice(user_agents)
        cmd = [
            "curl", "-s", "-x", proxy,
            "-A", user_agent,
            "https://api.bringyour.com/my-ip-info"
        ]

        try:
            response = subprocess.check_output(cmd, timeout=10).decode("utf-8")
        except subprocess.TimeoutExpired:
            with lock:
                print(f"[✗] {proxy} | Timeout")
            return
        except Exception as e:
            with lock:
                print(f"[✗] {proxy} | Error: {str(e)}")
            return

        try:
            data = json.loads(response)
            info = data.get("info", {})
            ip = info.get("ip", "")
            country = info.get("location", {}).get("country", {}).get("name", "")
            vpn = info.get("privacy", {}).get("vpn", "")
            proxy_flag = info.get("privacy", {}).get("proxy", "")
            tor = info.get("privacy", {}).get("tor", "")
            relay = info.get("privacy", {}).get("relay", "")
            hosting = info.get("privacy", {}).get("hosting", "")
            service = info.get("privacy", {}).get("service", "")

            if not ip:
                raise ValueError("Empty IP")

            result_line = f"[✓] {proxy} | IP: {ip} | Country: {country} | VPN: {vpn} | Proxy: {proxy_flag} | TOR: {tor} | Relay: {relay} | Hosting: {hosting} | Service: {service}"

            with lock:
                if proxy not in printed:
                    printed.add(proxy)
                    print(result_line)
                    with open(output_file, "a") as out:
                        out.write(result_line + "\n")
        except Exception:
            with lock:
                print(f"[✗] {proxy} | Invalid response")

def main():
    threads = []
    open(output_file, "w").close()  # clear output file

    for proxy in proxies:
        t = threading.Thread(target=check_proxy, args=(proxy,))
        t.start()
        threads.append(t)

    for t in threads:
        t.join()

if __name__ == "__main__":
    main()
