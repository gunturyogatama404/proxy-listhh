import requests

def get_proxies():
    urls = [
        "https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/http.txt",
        "https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/http.txt",
        "https://raw.githubusercontent.com/mmpx12/proxy-list/master/http.txt",
    ]

    proxies = set()
    for url in urls:
        try:
            res = requests.get(url, timeout=10)
            for line in res.text.splitlines():
                line = line.strip()
                if line and ":" in line:
                    proxies.add(line)
        except:
            pass
    return proxies

if __name__ == "__main__":
    all_proxies = get_proxies()
    with open("proxies.txt", "w") as f:
        for proxy in all_proxies:
            f.write(proxy + "\n")
    print(f"✅ {len(all_proxies)} proxies saved to proxies.txt")
