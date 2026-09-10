#!/usr/bin/env python3
"""Larch REST API helper script."""
import sys
import os
import json
import urllib.request
import urllib.error

BASE_URL = "https://larch.ink"

def get_key():
    key_file = os.path.expanduser("~/.config/larch/key")
    if os.path.exists(key_file):
        with open(key_file, "r") as f:
            return f.read().strip()
    key = os.environ.get("LARCH_API_KEY")
    if key:
        return key.strip()
    sys.stderr.write("Error: Larch key not found in ~/.config/larch/key or LARCH_API_KEY env.\n")
    sys.exit(1)

def request(path, method="GET", data=None, etag=None):
    url = f"{BASE_URL}{path}" if path.startswith("/") else f"{BASE_URL}/{path}"
    headers = {
        "Authorization": f"Bearer {get_key()}",
        "Accept": "application/json"
    }
    if data is not None:
        headers["Content-Type"] = "application/json"
        body = json.dumps(data).encode("utf-8")
    else:
        body = None
    if etag:
        headers["If-Match"] = etag

    req = urllib.request.Request(url, data=body, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            content = resp.read()
            etag_header = resp.headers.get("ETag")
            if resp.headers.get_content_type() == "application/json":
                parsed = json.loads(content.decode("utf-8"))
                if etag_header:
                    if isinstance(parsed, dict):
                        parsed["_etag"] = etag_header
                return parsed
            return content.decode("utf-8", errors="replace")
    except urllib.error.HTTPError as e:
        err_msg = e.read().decode("utf-8", errors="replace")
        sys.stderr.write(f"HTTP {e.code} error: {err_msg}\n")
        sys.exit(1)
    except Exception as e:
        sys.stderr.write(f"Request failed: {e}\n")
        sys.exit(1)

def main():
    if len(sys.argv) < 2:
        print("Usage: larch-api.py <command> [args...]")
        print("Commands:")
        print("  projects                  List projects")
        print("  resolve <id>              Resolve Larch ID")
        print("  project <projectId>       Get project details")
        print("  boards <projectId>        List boards")
        print("  characters <projectId>    List characters")
        print("  preview <projectId>       Get preview URL")
        print("  raw <METHOD> <path> [json] Make raw REST call")
        sys.exit(0)

    cmd = sys.argv[1]
    if cmd == "projects":
        res = request("/api/agent/projects")
        print(json.dumps(res, ensure_ascii=False, indent=2))
    elif cmd == "resolve":
        if len(sys.argv) < 3:
            sys.stderr.write("Usage: larch-api.py resolve <id>\n")
            sys.exit(1)
        res = request(f"/api/agent/resolve/{sys.argv[2]}")
        print(json.dumps(res, ensure_ascii=False, indent=2))
    elif cmd == "project":
        if len(sys.argv) < 3:
            sys.stderr.write("Usage: larch-api.py project <projectId>\n")
            sys.exit(1)
        res = request(f"/api/agent/projects/{sys.argv[2]}")
        print(json.dumps(res, ensure_ascii=False, indent=2))
    elif cmd == "boards":
        if len(sys.argv) < 3:
            sys.stderr.write("Usage: larch-api.py boards <projectId>\n")
            sys.exit(1)
        res = request(f"/api/agent/projects/{sys.argv[2]}/boards")
        print(json.dumps(res, ensure_ascii=False, indent=2))
    elif cmd == "characters":
        if len(sys.argv) < 3:
            sys.stderr.write("Usage: larch-api.py characters <projectId>\n")
            sys.exit(1)
        res = request(f"/api/agent/projects/{sys.argv[2]}/characters")
        print(json.dumps(res, ensure_ascii=False, indent=2))
    elif cmd == "preview":
        if len(sys.argv) < 3:
            sys.stderr.write("Usage: larch-api.py preview <projectId>\n")
            sys.exit(1)
        res = request(f"/api/agent/projects/{sys.argv[2]}/preview")
        print(json.dumps(res, ensure_ascii=False, indent=2))
    elif cmd == "raw":
        if len(sys.argv) < 4:
            sys.stderr.write("Usage: larch-api.py raw <METHOD> <path> [json_payload]\n")
            sys.exit(1)
        method = sys.argv[2].upper()
        path = sys.argv[3]
        payload = json.loads(sys.argv[4]) if len(sys.argv) > 4 else None
        res = request(path, method=method, data=payload)
        if isinstance(res, (dict, list)):
            print(json.dumps(res, ensure_ascii=False, indent=2))
        else:
            print(res)
    else:
        sys.stderr.write(f"Unknown command: {cmd}\n")
        sys.exit(1)

if __name__ == "__main__":
    main()
