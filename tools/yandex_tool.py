import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

AUTH_FILE = os.path.join(os.path.expanduser("~"), ".local", "share", "opencode", "mcp-auth.json")
OWN_FILE = os.path.join(os.path.expanduser("~"), ".local", "share", "opencode", "yandex_own.json")
MCP_URL = "https://mcp.becbt.tech/mcp"
TOKEN_URL = "https://oauth.yandex.ru/token"
AUTHORIZE_URL = "https://oauth.yandex.ru/authorize"
METRIKA_MGMT = "https://api-metrika.yandex.net/management/v1"
METRIKA_STAT = "https://api-metrika.yandex.net/stat/v1/data"
WEBMASTER = "https://api.webmaster.yandex.net/v4"

DEFAULT_REDIRECT = "https://oauth.yandex.ru/verification_code"
DEFAULT_SCOPE = "metrika:read webmaster"


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


def out(obj):
    print(json.dumps(obj, ensure_ascii=False, indent=2))


def post_form(url, data):
    body = urllib.parse.urlencode(data).encode()
    req = urllib.request.Request(url, data=body,
                                 headers={"Content-Type": "application/x-www-form-urlencoded"})
    with urllib.request.urlopen(req, timeout=60) as resp:
        return json.loads(resp.read().decode())


def load_own():
    if not os.path.exists(OWN_FILE):
        return {}
    with open(OWN_FILE, encoding="utf-8") as fh:
        return json.load(fh)


def save_own(cfg):
    with open(OWN_FILE, "w", encoding="utf-8") as fh:
        json.dump(cfg, fh, ensure_ascii=False, indent=2)


def refresh_own(cfg):
    tokens = cfg.get("tokens", {})
    refresh = tokens.get("refreshToken")
    client_id = cfg.get("client_id")
    client_secret = cfg.get("client_secret")
    if not (refresh and client_id and client_secret):
        raise RuntimeError("no refresh token / client credentials in config. run 'oauth url' then 'oauth code'")
    data = post_form(TOKEN_URL, {
        "grant_type": "refresh_token",
        "refresh_token": refresh,
        "client_id": client_id,
        "client_secret": client_secret,
    })
    tokens["accessToken"] = data["access_token"]
    if data.get("refresh_token"):
        tokens["refreshToken"] = data["refresh_token"]
    tokens["expiresAt"] = int(time.time()) + int(data.get("expires_in", 3600))
    save_own(cfg)
    return cfg


def own_token(cfg):
    tokens = cfg.get("tokens", {})
    exp = tokens.get("expiresAt") or 0
    if tokens.get("accessToken") and time.time() < exp - 60:
        return tokens["accessToken"]
    return refresh_own(cfg)["tokens"]["accessToken"]


def own_request(path, token=None, params=None, cfg=None):
    cfg = cfg or load_own()
    token = token or own_token(cfg)
    url = path
    if params:
        url = path + "?" + urllib.parse.urlencode(params, doseq=True)
    req = urllib.request.Request(url, headers={
        "Authorization": "OAuth " + token,
        "Content-Type": "application/json",
    })
    with urllib.request.urlopen(req, timeout=60) as resp:
        return json.loads(resp.read().decode())


def mcp_refresh_if_needed(entry):
    tokens = entry.get("tokens", {})
    exp = tokens.get("expiresAt") or 0
    if time.time() * 1000 < exp - 60000 and tokens.get("accessToken"):
        return entry
    if not tokens.get("refreshToken"):
        raise RuntimeError("token expired, no refresh token. Re-auth needed.")
    if not becbt_secret():
        raise RuntimeError("BECBT client secret not found (env BECBT_CLIENT_SECRET or opencode.jsonc)")
    data = post_form("https://mcp.becbt.tech/auth/realms/yandex-mcp/protocol/openid-connect/token", {
        "grant_type": "refresh_token",
        "refresh_token": tokens["refreshToken"],
        "client_id": "yandex-chatgpt",
        "client_secret": becbt_secret(),
    })
    tokens["accessToken"] = data["access_token"]
    if data.get("refresh_token"):
        tokens["refreshToken"] = data["refresh_token"]
    tokens["expiresAt"] = int(time.time() * 1000) + int(data.get("expires_in", 3600)) * 1000
    save_becbt_token(entry)
    return entry


def save_becbt_token(entry):
    with open(AUTH_FILE, encoding="utf-8") as fh:
        data = json.load(fh)
    data["yandex"] = entry
    with open(AUTH_FILE, "w", encoding="utf-8") as fh:
        json.dump(data, fh, ensure_ascii=False, indent=2)


def mcp_call(method, payload):
    with open(AUTH_FILE, encoding="utf-8") as fh:
        entry = json.load(fh)["yandex"]
    entry = mcp_refresh_if_needed(entry)
    cc = entry["tokens"]["accessToken"]
    req = {"jsonrpc": "2.0", "id": 1, "method": method, "params": payload}
    rq = urllib.request.Request(MCP_URL,
                                data=json.dumps(req).encode(),
                                headers={"Content-Type": "application/json",
                                         "Accept": "application/json, text/event-stream",
                                         "Authorization": "Bearer " + cc})
    try:
        with urllib.request.urlopen(rq, timeout=120) as resp:
            body = resp.read().decode()
            ctype = resp.headers.get("Content-Type", "")
    except urllib.error.HTTPError as e:
        body = e.read().decode()
        ctype = e.headers.get("Content-Type", "")
    if "text/event-stream" in ctype:
        for line in body.splitlines():
            if line.startswith("data:"):
                try:
                    return json.loads(line[5:].strip())
                except Exception:
                    pass
    try:
        return json.loads(body)
    except Exception:
        return {"raw": body[:2000]}


def check_mcp(res):
    sc = (res.get("result") or {}).get("structuredContent") or {}
    if res.get("error"):
        raise RuntimeError("mcp error: " + json.dumps(res["error"], ensure_ascii=False))
    if sc.get("error"):
        raise RuntimeError("mcp error: " + json.dumps(sc["error"], ensure_ascii=False))
    return sc


def ensure_own(cfg):
    if not cfg.get("tokens", {}).get("accessToken"):
        raise RuntimeError("no OAuth token. run 'oauth url', then 'oauth code <CODE>'")


def cmd_oauth_url(args):
    cfg = load_own()
    client_id = args.client_id or cfg.get("client_id")
    redirect = args.redirect_uri or cfg.get("redirect_uri") or DEFAULT_REDIRECT
    scope = args.scope or DEFAULT_SCOPE
    if not client_id:
        raise RuntimeError("client_id required. create app at https://oauth.yandex.ru/ or pass --client-id")
    q = urllib.parse.urlencode({
        "response_type": "code",
        "client_id": client_id,
        "redirect_uri": redirect,
        "scope": scope,
    })
    print(AUTHORIZE_URL + "?" + q)
    print("\nafter auth, copy code from redirect and run: oauth code <CODE>")


def cmd_oauth_code(args):
    cfg = load_own()
    client_id = args.client_id or cfg.get("client_id")
    client_secret = args.client_secret or cfg.get("client_secret")
    redirect = args.redirect_uri or cfg.get("redirect_uri") or DEFAULT_REDIRECT
    if args.save_client_id:
        cfg["client_id"] = client_id
    if args.save_client_secret and client_secret:
        cfg["client_secret"] = client_secret
    data = post_form(TOKEN_URL, {
        "grant_type": "authorization_code",
        "code": args.code,
        "client_id": client_id,
        "client_secret": client_secret or "",
        "redirect_uri": redirect,
    })
    if "error" in data:
        raise RuntimeError(json.dumps(data, ensure_ascii=False))
    cfg["tokens"] = {
        "accessToken": data["access_token"],
        "refreshToken": data.get("refresh_token"),
        "expiresAt": int(time.time()) + int(data.get("expires_in", 3600)),
        "scope": data.get("scope"),
    }
    save_own(cfg)
    out({"saved": OWN_FILE, "scope": data.get("scope")})


def cmd_metrika_counters(args):
    cfg = load_own()
    ensure_own(cfg)
    params = {}
    if args.search:
        params["search_string"] = args.search
    params["per_page"] = args.limit or 1000
    data = own_request(METRIKA_MGMT + "/counters", params=params, cfg=cfg)
    counters = data.get("counters", [])
    out([{"id": c["id"], "site": c.get("site2") or c.get("site"),
          "name": c.get("name"), "status": c.get("status"), "type": c.get("type")} for c in counters])


def cmd_metrika_report(args):
    cfg = load_own()
    ensure_own(cfg)
    params = {
        "ids": args.counter,
        "metrics": args.metrics,
        "date1": args.date1,
        "date2": args.date2,
        "accuracy": args.accuracy or "high",
    }
    if args.dimensions:
        params["dimensions"] = args.dimensions
    if args.filters:
        params["filters"] = args.filters
    if args.sort:
        params["sort"] = args.sort
    if args.limit:
        params["limit"] = args.limit
    data = own_request(METRIKA_STAT, params=params, cfg=cfg)
    out(data)


def cmd_metrika_traffic(args):
    cfg = load_own()
    ensure_own(cfg)
    params = {
        "ids": args.counter,
        "metrics": "ym:s:visits,ym:s:users,ym:s:pageviews,ym:s:bounceRate,ym:s:avgVisitDurationSeconds",
        "dimensions": "ym:s:date",
        "date1": args.date1,
        "date2": args.date2,
        "sort": "ym:s:date",
        "accuracy": args.accuracy or "high",
    }
    if args.limit:
        params["limit"] = args.limit
    data = own_request(METRIKA_STAT, params=params, cfg=cfg)
    out(data)


def cmd_metrika_sources(args):
    cfg = load_own()
    ensure_own(cfg)
    params = {
        "ids": args.counter,
        "metrics": "ym:s:visits,ym:s:users,ym:s:bounceRate",
        "dimensions": "ym:s:lastTrafficSource",
        "date1": args.date1,
        "date2": args.date2,
        "sort": "-ym:s:visits",
        "accuracy": args.accuracy or "high",
    }
    if args.limit:
        params["limit"] = args.limit
    data = own_request(METRIKA_STAT, params=params, cfg=cfg)
    out(data)


def cmd_metrika_conversion(args):
    cfg = load_own()
    ensure_own(cfg)
    if args.goal:
        g = args.goal
        metric = f"ym:gv:goal{g}reaches,ym:gv:goal{g}visits,ym:gv:goal{g}conversionRate"
    else:
        metric = "ym:gv:goalsReaches,ym:gv:goalsVisits,ym:gv:goalsConversionRate"
    params = {
        "ids": args.counter,
        "metrics": metric,
        "dimensions": "ym:s:date",
        "date1": args.date1,
        "date2": args.date2,
        "sort": "ym:s:date",
        "accuracy": args.accuracy or "high",
    }
    if args.limit:
        params["limit"] = args.limit
    data = own_request(METRIKA_STAT, params=params, cfg=cfg)
    out(data)


def cmd_webmaster_user(args):
    cfg = load_own()
    ensure_own(cfg)
    out(own_request(WEBMASTER + "/user", cfg=cfg))


def cmd_webmaster_hosts(args):
    cfg = load_own()
    ensure_own(cfg)
    uid = own_request(WEBMASTER + "/user", cfg=cfg)["user_id"]
    data = own_request(f"{WEBMASTER}/user/{uid}/hosts", cfg=cfg)
    out(data)


def wm_user_id(cfg):
    return own_request(WEBMASTER + "/user", cfg=cfg)["user_id"]


def wm_host_path(host):
    return urllib.parse.quote(host, safe="")


def cmd_webmaster_queries(args):
    cfg = load_own()
    ensure_own(cfg)
    uid = wm_user_id(cfg)
    params = {"limit": args.limit or 100}
    if args.order_by:
        params["order_by"] = args.order_by.upper()
    if args.indicators:
        params["query_indicator"] = [x.strip() for x in args.indicators.split(",") if x.strip()]
    if args.date_from:
        params["date_from"] = args.date_from
    if args.date_to:
        params["date_to"] = args.date_to
    data = own_request(f"{WEBMASTER}/user/{uid}/hosts/{wm_host_path(args.host)}/search-queries/popular",
                       params=params, cfg=cfg)
    out(data)


def cmd_webmaster_query_stats(args):
    cfg = load_own()
    ensure_own(cfg)
    uid = wm_user_id(cfg)
    params = {}
    if args.indicators:
        params["query_indicator"] = [x.strip() for x in args.indicators.split(",") if x.strip()]
    if args.date_from:
        params["date_from"] = args.date_from
    if args.date_to:
        params["date_to"] = args.date_to
    if args.query:
        url = f"{WEBMASTER}/user/{uid}/hosts/{wm_host_path(args.host)}/search-queries/{args.query}/history"
    else:
        url = f"{WEBMASTER}/user/{uid}/hosts/{wm_host_path(args.host)}/search-queries/all/history"
    data = own_request(url, params=params, cfg=cfg)
    out(data)


def cmd_webmaster_indexing(args):
    cfg = load_own()
    ensure_own(cfg)
    uid = wm_user_id(cfg)
    params = {}
    if args.date_from:
        params["date_from"] = args.date_from
    if args.date_to:
        params["date_to"] = args.date_to
    data = own_request(f"{WEBMASTER}/user/{uid}/hosts/{wm_host_path(args.host)}/indexing/history",
                       params=params, cfg=cfg)
    out(data)


def cmd_webmaster_sitemaps(args):
    cfg = load_own()
    ensure_own(cfg)
    uid = wm_user_id(cfg)
    params = {"limit": args.limit or 20}
    if args.from_id:
        params["from"] = args.from_id
    data = own_request(f"{WEBMASTER}/user/{uid}/hosts/{wm_host_path(args.host)}/sitemaps",
                       params=params, cfg=cfg)
    out(data)


def cmd_wordstat_top(args):
    params = {"phrase": args.phrase, "num_phrases": args.num or 50}
    if args.regions:
        params["regions"] = [x.strip() for x in args.regions.split(",") if x.strip()]
    sc = check_mcp(mcp_call("tools/call", {"name": "wordstat_get_top",
                                           "arguments": params}))
    out(sc.get("data") or {"error": sc.get("error")})


def cmd_wordstat_dynamics(args):
    params = {"phrase": args.phrase,
              "period": args.period,
              "from_date": args.from_date,
              "to_date": args.to_date}
    if args.regions:
        params["regions"] = [x.strip() for x in args.regions.split(",") if x.strip()]
    sc = check_mcp(mcp_call("tools/call", {"name": "wordstat_get_dynamics",
                                           "arguments": params}))
    out(sc.get("data") or {"error": sc.get("error")})


def cmd_wordstat_regions(args):
    params = {}
    if args.limit:
        params["limit"] = args.limit
    if args.offset:
        params["offset"] = args.offset
    if args.search:
        params["search"] = args.search
    sc = check_mcp(mcp_call("tools/call", {"name": "wordstat_get_regions_tree",
                                           "arguments": params}))
    out(sc.get("data") or sc)


def main():
    p = argparse.ArgumentParser(prog="yandex_tool",
                                description="Yandex tools: wordstat via becbt MCP, Metrika/Webmaster via own OAuth")
    sub = p.add_subparsers(dest="cmd", required=True)

    po = sub.add_parser("oauth", help="Metrika/Webmaster OAuth flow")
    po2 = po.add_subparsers(dest="oauth_cmd", required=True)
    pu = po2.add_parser("url", help="print authorize URL")
    pu.add_argument("--client-id")
    pu.add_argument("--redirect-uri")
    pu.add_argument("--scope", default=DEFAULT_SCOPE)
    pu.set_defaults(fn=cmd_oauth_url)
    pc = po2.add_parser("code", help="exchange authorization code for token")
    pc.add_argument("code")
    pc.add_argument("--client-id")
    pc.add_argument("--client-secret")
    pc.add_argument("--redirect-uri")
    pc.add_argument("--save-client-id", action="store_true", help="persist client_id in config")
    pc.add_argument("--save-client-secret", action="store_true", help="persist client_secret in config")
    pc.set_defaults(fn=cmd_oauth_code)

    pm = sub.add_parser("metrika", help="Metrika via own OAuth")
    pm2 = pm.add_subparsers(dest="metrika_cmd", required=True)
    pc1 = pm2.add_parser("counters")
    pc1.add_argument("--search")
    pc1.add_argument("--limit", type=int)
    pc1.set_defaults(fn=cmd_metrika_counters)
    pr = pm2.add_parser("report")
    pr.add_argument("--counter", required=True)
    pr.add_argument("--metrics", required=True)
    pr.add_argument("--dimensions")
    pr.add_argument("--date1", required=True)
    pr.add_argument("--date2", required=True)
    pr.add_argument("--filters")
    pr.add_argument("--sort")
    pr.add_argument("--limit", type=int)
    pr.add_argument("--accuracy")
    pr.set_defaults(fn=cmd_metrika_report)
    pt = pm2.add_parser("traffic")
    pt.add_argument("--counter", required=True)
    pt.add_argument("--date1", required=True)
    pt.add_argument("--date2", required=True)
    pt.add_argument("--limit", type=int)
    pt.add_argument("--accuracy")
    pt.set_defaults(fn=cmd_metrika_traffic)
    ps = pm2.add_parser("sources")
    ps.add_argument("--counter", required=True)
    ps.add_argument("--date1", required=True)
    ps.add_argument("--date2", required=True)
    ps.add_argument("--limit", type=int)
    ps.add_argument("--accuracy")
    ps.set_defaults(fn=cmd_metrika_sources)
    pc2 = pm2.add_parser("conversion")
    pc2.add_argument("--counter", required=True)
    pc2.add_argument("--goal", help="goal id; empty = all goals")
    pc2.add_argument("--date1", required=True)
    pc2.add_argument("--date2", required=True)
    pc2.add_argument("--limit", type=int)
    pc2.add_argument("--accuracy")
    pc2.set_defaults(fn=cmd_metrika_conversion)

    pw = sub.add_parser("webmaster", help="Webmaster via own OAuth")
    pw2 = pw.add_subparsers(dest="webmaster_cmd", required=True)
    pw1 = pw2.add_parser("user")
    pw1.set_defaults(fn=cmd_webmaster_user)
    pwh = pw2.add_parser("hosts")
    pwh.set_defaults(fn=cmd_webmaster_hosts)
    pwq = pw2.add_parser("queries")
    pwq.add_argument("--host", required=True)
    pwq.add_argument("--order-by")
    pwq.add_argument("--indicators")
    pwq.add_argument("--date-from")
    pwq.add_argument("--date-to")
    pwq.add_argument("--limit", type=int)
    pwq.set_defaults(fn=cmd_webmaster_queries)
    pws = pw2.add_parser("query-stats")
    pws.add_argument("--host", required=True)
    pws.add_argument("--query")
    pws.add_argument("--indicators")
    pws.add_argument("--date-from")
    pws.add_argument("--date-to")
    pws.set_defaults(fn=cmd_webmaster_query_stats)
    pwi = pw2.add_parser("indexing")
    pwi.add_argument("--host", required=True)
    pwi.add_argument("--date-from")
    pwi.add_argument("--date-to")
    pwi.set_defaults(fn=cmd_webmaster_indexing)
    pwsi = pw2.add_parser("sitemaps")
    pwsi.add_argument("--host", required=True)
    pwsi.add_argument("--limit", type=int)
    pwsi.add_argument("--from-id")
    pwsi.set_defaults(fn=cmd_webmaster_sitemaps)

    ww = sub.add_parser("wordstat", help="Wordstat via becbt MCP (shared token)")
    ww2 = ww.add_subparsers(dest="wordstat_cmd", required=True)
    wrt = ww2.add_parser("top")
    wrt.add_argument("phrase")
    wrt.add_argument("--regions", help="comma list, e.g. 225,213")
    wrt.add_argument("--num", type=int)
    wrt.set_defaults(fn=cmd_wordstat_top)
    wrd = ww2.add_parser("dynamics")
    wrd.add_argument("phrase")
    wrd.add_argument("--period", default="monthly")
    wrd.add_argument("--from-date", required=True)
    wrd.add_argument("--to-date", required=True)
    wrd.add_argument("--regions", help="comma list")
    wrd.set_defaults(fn=cmd_wordstat_dynamics)
    wrr = ww2.add_parser("regions")
    wrr.add_argument("--search")
    wrr.add_argument("--limit", type=int)
    wrr.add_argument("--offset", type=int)
    wrr.set_defaults(fn=cmd_wordstat_regions)

    args = p.parse_args()
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    try:
        args.fn(args)
    except urllib.error.HTTPError as e:
        raise SystemExit(f"HTTP {e.code}: {e.read().decode(errors='replace')}")


if __name__ == "__main__":
    main()