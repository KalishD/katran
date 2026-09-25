import json
import os
import time
import urllib.parse
import urllib.request

MCP_URL = "https://mcp.becbt.tech/mcp"
TOKEN_URL = "https://mcp.becbt.tech/auth/realms/yandex-mcp/protocol/openid-connect/token"
AUTH_FILE = os.path.join(os.path.expanduser("~"), ".local", "share", "opencode", "mcp-auth.json")


def becbt_secret():
    secret = os.environ.get("BECBT_CLIENT_SECRET")
    if secret:
        return secret
    cfg_path = os.path.join(os.path.expanduser("~"), ".config", "opencode", "opencode.jsonc")
    if os.path.exists(cfg_path):
        import re
        with open(cfg_path, encoding="utf-8") as fh:
            m = re.search(r'"clientSecret":\s*"([^"]+)"', fh.read())
        if m:
            return m.group(1)
    return ""


def load_auth():
    with open(AUTH_FILE, encoding="utf-8") as fh:
        return json.load(fh)["yandex"]


def save_auth(entry):
    with open(AUTH_FILE, encoding="utf-8") as fh:
        data = json.load(fh)
    data["yandex"] = entry
    with open(AUTH_FILE, "w", encoding="utf-8") as fh:
        json.dump(data, fh, indent=2, ensure_ascii=False)


def post(url, body):
    req = urllib.request.Request(url, data=urllib.parse.urlencode(body).encode(),
                                 headers={"Content-Type": "application/x-www-form-urlencoded"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode())


def refresh_if_needed(entry):
    tokens = entry.get("tokens", {})
    exp = tokens.get("expiresAt") or 0
    if time.time() * 1000 < exp - 60000 and tokens.get("accessToken"):
        return entry
    if not tokens.get("refreshToken"):
        raise RuntimeError("token expired, no refresh token. Re-auth needed.")
    client_secret = becbt_secret()
    if not client_secret:
        raise RuntimeError("BECBT client secret not found (env BECBT_CLIENT_SECRET or opencode.jsonc)")
    data = post(TOKEN_URL, {
        "grant_type": "refresh_token",
        "refresh_token": tokens["refreshToken"],
        "client_id": "yandex-chatgpt",
        "client_secret": client_secret,
    })
    tokens["accessToken"] = data["access_token"]
    if data.get("refresh_token"):
        tokens["refreshToken"] = data["refresh_token"]
    tokens["expiresAt"] = int(time.time() * 1000) + int(data.get("expires_in", 3600)) * 1000
    tokens["scope"] = data.get("scope")
    save_auth(entry)
    return entry


entry = refresh_if_needed(load_auth())
cc = entry["tokens"]["accessToken"]


def mcp_call(method, payload, rid=1):
    req = {"jsonrpc": "2.0", "id": rid, "method": method, "params": payload}
    rq = urllib.request.Request(MCP_URL, data=json.dumps(req).encode(),
                                headers={"Content-Type": "application/json",
                                         "Accept": "application/json, text/event-stream",
                                         "Authorization": f"Bearer {cc}"})
    try:
        with urllib.request.urlopen(rq, timeout=120) as resp:
            body = resp.read().decode()
            args = resp.headers.get("Content-Type", "")
    except urllib.error.HTTPError as e:
        body = e.read().decode()
        args = e.headers.get("Content-Type", "")
    if "text/event-stream" in str(args):
        for line in body.splitlines():
            if line.startswith("data:"):
                try:
                    return json.loads(line[5:].strip())
                except Exception:
                    pass
        return {"raw": body[:2000]}
    try:
        return json.loads(body)
    except Exception:
        return {"raw": body[:2000]}


TERMS = [
    "collet", "пневмошлифмашина цанговая",
    "collet_opt", "шлифмашина пневматическая цанговая",
    "face", "торцевая пневмошлифмашина",
    "face2", "торцевая шлифмашина пневматическая",
    "corner", "зачистная угловая машина пневматическая",
    "osv", "пневматическая шлифовальная машина",
    "tramb", "пневматическая трамбовка",
    "tramb2", "пневмотрамбовка",
    "tramb_dozh", "трамбовка пневматическая",
    "chisel", "пневмозубило",
    "hammer", "рубильный молоток пневматический",
    "hammer2", "пневматический рубильный молоток",
    "privod", "пневмопривод",
    "remont", "ремонт пневмоинструмента",
    "vybor", "как выбрать пневмошлифмашину",
    "kompressor", "компрессор для пневмошлифмашины",
]

D = r"C:\Users\KDGHome\AppData\Local\Temp\opencode\ws_prod"
os.makedirs(D, exist_ok=True)

summary = {}
for i in range(0, len(TERMS), 2):
    key, phrase = TERMS[i], TERMS[i + 1]
    outf = os.path.join(D, f"_t_{key}.json")
    if not os.path.exists(outf):
        res = mcp_call("tools/call", {"name": "wordstat_get_top",
                                      "arguments": {"phrase": phrase, "regions": ["225"],
                                                    "num_phrases": 50, "limit": 50}}, rid=3)
        with open(outf, "w", encoding="utf-8") as fh:
            json.dump(res, fh, ensure_ascii=False)
    d = json.load(open(outf, encoding="utf-8"))
    sc = d.get("result", {}).get("structuredContent", {})
    data = sc.get("data", {})
    total = data.get("totalCount")
    results = data.get("results", [])
    assoc = data.get("associations", [])
    print(f"{key}: total={total} results={len(results)} assoc={len(assoc)}")
    for r in results:
        print("   ", r.get("phrase"), "=", r.get("count"))
    summary[key] = {"total": total, "results": results, "associations": assoc}

with open(os.path.join(D, "_summary.json"), "w", encoding="utf-8") as fh:
    json.dump(summary, fh, ensure_ascii=False, indent=2)
print("SALVAGE DONE")