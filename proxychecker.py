import argparse
import threading
import requests
import random

with open("user_agents.txt", "r") as f:
    user_agents = [line.strip() for line in f if line.strip()]

lock = threading.Lock()
results = []

def check_proxy(proxy, timeout):
    proxies = {"http": proxy, "https": proxy}
    headers = {"User-Agent": random.choice(user_agents)}
    try:
        r = requests.get("https://api.bringyour.com/my-ip-info", headers=headers, proxies=proxies, timeout=timeout)
        if r.status_code == 200 and "ip" in r.text.lower():
            data = r.json()
            result = f"[✓] {proxy} | IP: {data.get('ip')} | Country: {data.get('country')} | VPN: {data.get('vpn')} | Proxy: {data.get('proxy')} | TOR: {data.get('tor')} | Relay: {data.get('relay')} | Hosting: {data.get('hosting')} | Service: {data.get('service', '')}"
            with lock:
                results.append(result)
            print(result)
    except Exception:
        pass

def main(file, output, timeout, threads):
    with open(file, "r") as f:
        proxies = [line.strip() for line in f if line.strip()]

    thread_list = []
    for proxy in proxies:
        if not proxy.startswith("http"):
            proxy = "http://" + proxy
        t = threading.Thread(target=check_proxy, args=(proxy, timeout))
        thread_list.append(t)
        t.start()
        if len(thread_list) >= threads:
            for th in thread_list:
                th.join()
            thread_list = []

    for t in thread_list:
        t.join()

    with open(output, "w") as f:
        for line in results:
            f.write(line + "\n")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-l", "--list", default="proxies.txt")
    parser.add_argument("-o", "--output", default="result.txt")
    parser.add_argument("-t", "--timeout", type=int, default=10)
    parser.add_argument("-th", "--threads", type=int, default=50)
    args = parser.parse_args()
    main(args.list, args.output, args.timeout, args.threads)
