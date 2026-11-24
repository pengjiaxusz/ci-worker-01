#!/usr/bin/env python3
"""Post a GitHub Commit Status back to TARGET_REPO."""
import json, os, sys, urllib.request, urllib.error

def main():
    if len(sys.argv) < 5:
        print("Usage: report_status.py <sha> <state> <context> <description> [target_url]", file=sys.stderr)
        sys.exit(2)
    sha, state, context, description = sys.argv[1:5]
    target_url = sys.argv[5] if len(sys.argv) > 5 else ""
    repo = os.environ["TARGET_REPO"]
    token = os.environ["TARGET_TOKEN"]

    payload = {
        "state": state,
        "context": context,
        "description": description[:140],
    }
    if target_url:
        payload["target_url"] = target_url

    req = urllib.request.Request(
        f"https://api.github.com/repos/{repo}/statuses/{sha}",
        data=json.dumps(payload).encode("utf-8"),
        method="POST",
        headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
            "Content-Type": "application/json",
            "X-GitHub-Api-Version": "2022-11-28",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            print(f"[status] {context} -> {state} (HTTP {r.status})")
    except urllib.error.HTTPError as e:
        print(f"[status] failed {e.code}: {e.read().decode()}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
