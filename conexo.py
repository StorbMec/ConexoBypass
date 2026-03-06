import requests
import json
import random
import string
import re
import urllib3
from urllib.parse import quote

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

DATABASE = "projects/daydashgames/databases/(default)"

HEADERS_POST = {
    "Host":                     "firestore.googleapis.com",
    "sec-ch-ua-platform":       '"Windows"',
    "user-agent":               "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36",
    "sec-ch-ua":                '"Not:A-Brand";v="99", "Brave";v="145", "Chromium";v="145"',
    "content-type":             "application/x-www-form-urlencoded",
    "sec-ch-ua-mobile":         "?0",
    "accept":                   "*/*",
    "sec-gpc":                  "1",
    "accept-language":          "pt-BR,pt;q=0.8",
    "origin":                   "https://conexo.ws",
    "sec-fetch-site":           "cross-site",
    "sec-fetch-mode":           "cors",
    "sec-fetch-dest":           "empty",
    "sec-fetch-storage-access": "none",
    "referer":                  "https://conexo.ws/",
    "priority":                 "u=1, i",
    "pragma":                   "no-cache",
    "cache-control":            "no-cache",
}

HEADERS_GET = {k: v for k, v in HEADERS_POST.items() if k != "content-type"}

BASE_URL = "https://firestore.googleapis.com/google.firestore.v1.Firestore/Listen/channel"

def zx():
    return "".join(random.choices(string.ascii_lowercase + string.digits, k=12))

def rid():
    return str(random.randint(10000, 99999))

def create_session(appcheck: str, doc_id: str) -> tuple[str, str]:
    inner_headers = (
        "X-Goog-Api-Client:gl-js/ fire/10.4.0\r\n"
        "Content-Type:text/plain\r\n"
        "X-Firebase-GMPID:1:689008611670:web:45c4d4dbce26e56deb46f7\r\n"
        f"x-firebase-appcheck:{appcheck}\r\n"
    )

    req0_data = json.dumps({
        "database": DATABASE,
        "addTarget": {
            "documents": {
                "documents": [f"{DATABASE}/documents/conexo-daily-pt/{doc_id}"]
            },
            "targetId": 2
        }
    })

    body = f"headers={quote(inner_headers)}&count=1&ofs=0&req0___data__={quote(req0_data)}"
    url  = f"{BASE_URL}?VER=8&database=projects%2Fdaydashgames%2Fdatabases%2F(default)&RID={rid()}&CVER=22&X-HTTP-Session-Id=gsessionid&zx={zx()}&t=1"

    resp = requests.post(url, headers=HEADERS_POST, data=body, verify=False, timeout=15)
    resp.raise_for_status()

    gsessionid = resp.headers["X-HTTP-Session-Id"]
    sid        = json.loads(resp.text.split("\n", 1)[1])[0][1][1]
    return gsessionid, sid

def fetch_puzzle(gsessionid: str, sid: str) -> str:
    url = (
        f"{BASE_URL}?gsessionid={gsessionid}"
        f"&VER=8&database=projects%2Fdaydashgames%2Fdatabases%2F(default)"
        f"&RID=rpc&SID={sid}&AID=0&CI=0&TYPE=xmlhttp&zx={zx()}&t=1"
    )

    with requests.get(url, headers=HEADERS_GET, stream=True, timeout=(10, 30), verify=False) as resp:
        resp.raise_for_status()
        buffer = ""
        for chunk in resp.iter_content(chunk_size=4096, decode_unicode=True):
            if chunk:
                buffer += chunk
                if "documentChange" in buffer:
                    break
    return buffer

def parse_groups(raw: str) -> list[dict]:
    for chunk in re.split(r"(?m)^\d+$", raw):
        chunk = chunk.strip()
        if not chunk:
            continue
        try:
            data = json.loads(chunk)
        except json.JSONDecodeError:
            continue
        for seq in data:
            if not isinstance(seq, list) or len(seq) < 2:
                continue
            for event in seq[1]:
                if not isinstance(event, dict):
                    continue
                fields = event.get("documentChange", {}).get("document", {}).get("fields", {})
                if "groups" not in fields:
                    continue
                groups = [
                    {
                        "number": int(g["mapValue"]["fields"]["number"]["integerValue"]),
                        "theme":  g["mapValue"]["fields"]["theme"]["stringValue"],
                        "words":  [w["stringValue"] for w in g["mapValue"]["fields"]["words"]["arrayValue"]["values"]],
                    }
                    for g in fields["groups"]["arrayValue"]["values"]
                ]
                return sorted(groups, key=lambda x: x["number"])
    return []

def main():
    print("=== Conexo Solver ===\n")
    print("DevTools → Network → POST channel → Payload → x-firebase-appcheck")
    appcheck = input("AppCheck token: ").strip()
    doc_id   = input("DOC_ID (ex: 887): ").strip()

    print("\nCriando sessão...")
    gsessionid, sid = create_session(appcheck, doc_id)

    print("Buscando puzzle...")
    raw    = fetch_puzzle(gsessionid, sid)
    groups = parse_groups(raw)

    if not groups:
        print("Nenhum grupo encontrado. Resposta bruta:")
        print(raw[:500])
        return

    print(f"\n=== Conexo #{doc_id} ===\n")
    for g in groups:
        print(f"Grupo {g['number']}: {g['theme']}")
        print(f"  {', '.join(g['words'])}\n")


if __name__ == "__main__":
    main()