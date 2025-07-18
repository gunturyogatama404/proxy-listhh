import requests

sources = [
    "https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/http.txt",
    "https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/http.txt",
    "https://raw.githubusercontent.com/mmpx12/proxy-list/master/http.txt",
    "https://raw.githubusercontent.com/roosterkid/openproxylist/main/HTTPS_RAW.txt",
    "https://raw.githubusercontent.com/ShiftyTR/Proxy-List/master/http.txt",
]

seen = set()
with open("proxies.txt", "w") as f:
    for url in sources:
        try:
            r = requests.get(url, timeout=10)
            for line in r.text.strip().split("\n"):
                line = line.strip()
                if line and line not in seen:
                    if not line.startswith("http"):
                        line = "http://" + line
                    f.write(line + "\n")
                    seen.add(line)
        except Exception as e:
            print(f"[!] Failed to fetch from {url}: {e}")
