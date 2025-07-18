import argparse
import random
import re
import threading
import urllib.request
from time import time

user_agents = []
with open("user_agents.txt", "r") as f:
    for line in f:
        user_agents.append(line.strip())


class Proxy:
    def __init__(self, method, proxy):
        if method.lower() not in ["http", "https"]:
            raise NotImplementedError("Only HTTP and HTTPS are supported")
        self.method = method.lower()
        self.proxy = proxy.strip()

    def is_valid(self):
        return re.match(r"\d{1,3}(?:\.\d{1,3}){3}:\d{2,5}$", self.proxy)

    def check(self, site, timeout, user_agent):
        proxy_handler = urllib.request.ProxyHandler({self.method: f"{self.method}://{self.proxy}"})
        opener = urllib.request.build_opener(proxy_handler)
        req = urllib.request.Request(site)
        req.add_header("User-Agent", user_agent)
        try:
            start_time = time()
            response = opener.open(req, timeout=timeout)
            end_time = time()
            info = response.read().decode(errors="ignore").strip().replace('\n', '')
            return True, end_time - start_time, info
        except Exception as e:
            return False, 0, str(e)

    def __str__(self):
        return self.proxy


def verbose_print(verbose, message):
    if verbose:
        print(message)


def check(file, output, timeout, method, site, verbose, random_user_agent):
    proxies = []
    with open(file, "r") as f:
        for line in f:
            proxies.append(Proxy(method, line.strip()))

    print(f"🔍 Checking {len(proxies)} proxies...\n")
    proxies = list(filter(lambda x: x.is_valid(), proxies))
    valid_results = []
    user_agent = random.choice(user_agents)

    lock = threading.Lock()

    def check_proxy(proxy):
        new_user_agent = random.choice(user_agents) if random_user_agent else user_agent
        valid, time_taken, result = proxy.check(site, timeout, new_user_agent)
        if valid:
            line = f"{proxy} | {round(time_taken, 2)}s | {result}"
            verbose_print(verbose, f"✅ {line}")
            with lock:
                valid_results.append(line)
        else:
            verbose_print(verbose, f"❌ {proxy} failed: {result}")

    threads = []
    for proxy in proxies:
        t = threading.Thread(target=check_proxy, args=(proxy,))
        threads.append(t)
        t.start()

    for t in threads:
        t.join()

    with open(output, "w") as f:
        for line in valid_results:
            f.write(line + "\n")

    print(f"\n🎯 Done! Found {len(valid_results)} valid proxies. Results saved to {output}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-t", "--timeout", type=int, default=15, help="Timeout for each proxy request")
    parser.add_argument("-p", "--proxy", default="http", help="Proxy type: http or https")
    parser.add_argument("-l", "--list", default="proxies.txt", help="Input proxy list file")
    parser.add_argument("-o", "--output", default="result.txt", help="Output result file")
    parser.add_argument("-s", "--site", default="https://api.bringyour.com/my-ip-info", help="Site to test proxy with")
    parser.add_argument("-v", "--verbose", action="store_true", help="Show detailed output")
    parser.add_argument("-r", "--random_agent", action="store_true", help="Use random User-Agent per proxy")
    args = parser.parse_args()

    check(
        file=args.list,
        output=args.output,
        timeout=args.timeout,
        method=args.proxy,
        site=args.site,
        verbose=args.verbose,
        random_user_agent=args.random_agent,
    )
