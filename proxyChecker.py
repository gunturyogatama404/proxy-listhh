import threading
import argparse
import random
import requests
import re

user_agents = []
with open("user_agents.txt", "r") as f:
    user_agents = [line.strip() for line in f if line.strip()]

lock = threading.Lock()
results = []

def is_valid_proxy(proxy):
    return re.match(r"\d{1,3}(?:\.\d{1,3}){3}:\d{2,5}$", proxy)

def check_proxy(proxy, timeout, verbose):
    try:
        proxy_url = f"http://{proxy}"
        headers = {"User-Agent": random.choice(user_agents)}
        r = requests.get("https://api.bringyour.com/my-ip-info", proxies={"http": proxy_url, "https": proxy_url}, headers=headers, timeout=timeout)
        if r.status_code == 200 and r.headers.get("Content-Type", "").startswith("application/json"):
            data = r.json()
            line = f"[✓] http://{proxy} | IP: {data.get('ip')} | Country: {data.get('country')} | VPN: {data.get('vpn')} | Proxy: {data.get('proxy')} | TOR: {data.get('tor')} | Relay: {data.get('relay')} | Hosting: {data.get('hosting')} | Service: {data.get('service', '')}"
            with lock:
                results.append(line)
            if verbose:
                print(line)
    except Exception as e:
        if verbose:
            print(f"[✗] {proxy} -> {e}")

def run_checker(input_file, output_file, timeout, verbose):
    with open(input_file, "r") as f:
        proxies = [line.strip() for line in f if is_valid_proxy(line.strip())]

    threads = []
    for proxy in proxies:
        t = threading.Thread(target=check_proxy, args=(proxy, timeout, verbose))
        t.start()
        threads.append(t)

    for t in threads:
        t.join()

    with open(output_file, "w") as f:
        for res in results:
            f.write(res + "\n")

    print(f"\n✅ Done. {len(results)} valid proxies saved to {output_file}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-l", "--list", default="proxies.txt", help="Input file")
    parser.add_argument("-o", "--output", default="result.txt", help="Output file")
    parser.add_argument("-t", "--timeout", type=int, default=10, help="Timeout per proxy")
    parser.add_argument("-v", "--verbose", action="store_true", help="Verbose output")
    args = parser.parse_args()

    run_checker(args.list, args.output, args.timeout, args.verbose)
