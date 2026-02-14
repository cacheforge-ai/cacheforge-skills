#!/usr/bin/env python3
"""CacheForge setup CLI — register, configure upstream, get your API key in 30 seconds."""

import argparse
import json
import os
import sys
import urllib.request
import urllib.error

# ── ANSI colors ──────────────────────────────────────────────────────────────

CYAN = "\033[36m"
GREEN = "\033[32m"
RED = "\033[31m"
YELLOW = "\033[33m"
BOLD = "\033[1m"
DIM = "\033[2m"
RESET = "\033[0m"

# ── Helpers ──────────────────────────────────────────────────────────────────

DEFAULT_BASE_URL = "https://app.anvil-ai.io"

def normalize_base_url(url: str) -> str:
    """Normalize a CacheForge base URL (accepts both with and without /v1)."""
    url = (url or "").strip().rstrip("/")
    if url.endswith("/v1"):
        url = url[:-3]
    return url.rstrip("/")


def get_base_url(args_base_url: str | None) -> str:
    """Resolve base URL from arg, env, or default."""
    url = args_base_url or os.environ.get("CACHEFORGE_BASE_URL") or DEFAULT_BASE_URL
    return normalize_base_url(url)


def box(title: str, lines: list[tuple[str, str]], color: str = CYAN) -> str:
    """Render a Unicode box with key-value lines."""
    # Calculate width from content
    content_lines = []
    for label, value in lines:
        content_lines.append(f"  {label}: {value}")

    max_width = max(len(title) + 4, *(len(l) for l in content_lines)) + 4
    width = max(max_width, 50)

    parts = []
    parts.append(f"{color}{BOLD}  {title}{RESET}")
    parts.append(f"{color}  {'─' * width}{RESET}")
    for label, value in lines:
        parts.append(f"{DIM}  {label}:{RESET} {GREEN}{value}{RESET}")
    parts.append(f"{color}  {'─' * width}{RESET}")
    return "\n".join(parts)


def draw_box(title: str, lines: list[tuple[str, str]], color: str = CYAN) -> str:
    """Render a framed Unicode box with box-drawing characters."""
    content_lines = []
    for label, value in lines:
        content_lines.append((f" {label}: ", f"{value} "))

    inner_widths = []
    for label_part, value_part in content_lines:
        inner_widths.append(len(label_part) + len(value_part))
    title_display = f" {title} "
    inner_widths.append(len(title_display))
    inner_width = max(max(inner_widths), 48)

    parts = []
    # Top border
    parts.append(f"{color}{BOLD}")
    parts.append(f"  ┌{'─' * inner_width}┐")
    parts.append(f"  │{title_display}{' ' * (inner_width - len(title_display))}│")
    parts.append(f"  ├{'─' * inner_width}┤")

    # Content lines
    for label_part, value_part in content_lines:
        raw = label_part + value_part
        padding = inner_width - len(raw)
        parts.append(
            f"  │{DIM}{label_part}{RESET}{color}{GREEN}{value_part}{RESET}"
            f"{color}{BOLD}{' ' * padding}│"
        )

    # Bottom border
    parts.append(f"  └{'─' * inner_width}┘")
    parts.append(f"{RESET}")
    return "\n".join(parts)


def http_post(url: str, payload: dict) -> dict:
    """POST JSON to a URL, return parsed response."""
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")
        try:
            detail = json.loads(body)
        except Exception:
            detail = {"raw": body}
        raise SystemExit(
            f"\n{RED}  Error {e.code} from {url}{RESET}\n"
            f"{DIM}  {json.dumps(detail, indent=2)}{RESET}\n"
        )
    except urllib.error.URLError as e:
        raise SystemExit(
            f"\n{RED}  Connection failed: {e.reason}{RESET}\n"
            f"{DIM}  URL: {url}{RESET}\n"
        )


def http_get(url: str, headers: dict | None = None) -> dict:
    """GET a URL with optional headers, return parsed response."""
    req = urllib.request.Request(url, headers=headers or {}, method="GET")
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")
        return {"_http_error": e.code, "_body": body}
    except urllib.error.URLError as e:
        raise SystemExit(
            f"\n{RED}  Connection failed: {e.reason}{RESET}\n"
            f"{DIM}  URL: {url}{RESET}\n"
        )


def detect_upstream_key() -> tuple[str, str] | None:
    """Auto-detect upstream provider from environment variables."""
    for env_var, kind, prefix_label in [
        ("OPENROUTER_API_KEY", "openrouter", "sk-or-"),
        ("ANTHROPIC_API_KEY", "anthropic", "sk-ant-"),
        ("OPENAI_API_KEY", "openai", "sk-"),
    ]:
        key = os.environ.get(env_var)
        if key:
            return (kind, key)
    return None


def infer_kind_from_key(key: str) -> str:
    """Infer upstream kind from API key prefix."""
    if key.startswith("sk-or-"):
        return "openrouter"
    if key.startswith("sk-ant-"):
        return "anthropic"
    if key.startswith("sk-"):
        return "openai"
    return "openai"  # default fallback


# ── Subcommands ──────────────────────────────────────────────────────────────


def cmd_provision(args: argparse.Namespace) -> None:
    """Register or authenticate and provision a CacheForge API key."""
    base_url = get_base_url(args.base_url)

    # Check if already provisioned
    existing_key = os.environ.get("CACHEFORGE_API_KEY")
    if existing_key and not args.email:
        print(f"\n{YELLOW}  CACHEFORGE_API_KEY is already set in your environment.{RESET}")
        print(f"{DIM}  Use 'validate' to check it, or pass --email to re-provision.{RESET}\n")
        return

    # Resolve email and password
    email = args.email
    password = args.password

    if not email:
        print(f"\n{RED}  --email is required for provisioning.{RESET}")
        print(f"{DIM}  Usage: setup.py provision --email you@example.com --password '...'{RESET}\n")
        raise SystemExit(1)

    if not password:
        print(f"\n{RED}  --password is required for provisioning.{RESET}")
        raise SystemExit(1)

    invite_code = (args.invite_code or os.environ.get("CACHEFORGE_INVITE_CODE") or "").strip()

    # Resolve upstream
    upstream_kind = args.upstream_kind
    upstream_key = args.upstream_key

    if not upstream_key:
        detected = detect_upstream_key()
        if detected:
            auto_kind, auto_key = detected
            upstream_kind = upstream_kind or auto_kind
            upstream_key = auto_key
            masked = auto_key[:8] + "..." + auto_key[-4:]
            print(f"\n{CYAN}  Auto-detected upstream:{RESET} {GREEN}{auto_kind}{RESET} ({DIM}{masked}{RESET})")
        else:
            print(f"\n{RED}  No upstream API key found.{RESET}")
            print(f"{DIM}  Pass --upstream-key or set OPENAI_API_KEY / OPENROUTER_API_KEY / ANTHROPIC_API_KEY{RESET}\n")
            raise SystemExit(1)

    if not upstream_kind:
        upstream_kind = infer_kind_from_key(upstream_key)
        print(f"{CYAN}  Inferred upstream kind:{RESET} {GREEN}{upstream_kind}{RESET}")

    # Call provision endpoint
    provision_url = f"{base_url}/api/provision"
    payload = {
        "email": email,
        "password": password,
        "upstream": {
            "kind": upstream_kind,
            "apiKey": upstream_key,
        },
    }
    if invite_code:
        payload["inviteCode"] = invite_code

    print(f"\n{CYAN}{BOLD}  Provisioning CacheForge account...{RESET}")
    print(f"{DIM}  POST {provision_url}{RESET}\n")

    result = http_post(provision_url, payload)

    # Verification-required flow: provisioning succeeded but key is not returned.
    if result.get("requiresVerification"):
        print(f"\n{YELLOW}{BOLD}  Email verification required.{RESET}")
        print(f"{DIM}  {result.get('message', 'Check your email to verify your account.')}{RESET}")
        if result.get("verificationUrl"):
            print(f"\n{CYAN}{BOLD}  Verification URL:{RESET}")
            print(f"  {result.get('verificationUrl')}\n")
        print(f"{DIM}  After verifying, rerun provision to mint an API key.{RESET}\n")
        return

    api_key = result.get("apiKey") or result.get("api_key") or result.get("key")
    tenant_id = result.get("tenantId") or result.get("tenant_id") or result.get("id", "")

    if not api_key:
        print(f"{RED}  Unexpected response — no API key returned.{RESET}")
        print(f"{DIM}  {json.dumps(result, indent=2)}{RESET}")
        raise SystemExit(1)

    # Success output
    print(draw_box(
        "CacheForge Ready",
        [
            ("API Key", api_key),
            ("Base URL", f"{base_url}/v1"),
            ("Tenant", str(tenant_id)),
            ("Upstream", upstream_kind),
        ],
        color=CYAN,
    ))

    print(f"\n{CYAN}{BOLD}  Next steps:{RESET}")
    print(f"{DIM}  Add these to your environment:{RESET}\n")
    print(f"  {GREEN}export OPENAI_BASE_URL={base_url}/v1{RESET}")
    print(f"  {GREEN}export OPENAI_API_KEY={api_key}{RESET}")
    print()


def cmd_validate(args: argparse.Namespace) -> None:
    """Validate an existing CacheForge setup by hitting the account info endpoint."""
    base_url = get_base_url(args.base_url)

    api_key = args.api_key or os.environ.get("CACHEFORGE_API_KEY")
    if not api_key:
        # Also check OPENAI_API_KEY if it looks like a CacheForge key
        oai_key = os.environ.get("OPENAI_API_KEY", "")
        if oai_key.startswith("cfk_"):
            api_key = oai_key

    if not api_key:
        print(f"\n{RED}  No API key found.{RESET}")
        print(f"{DIM}  Pass --api-key or set CACHEFORGE_API_KEY / OPENAI_API_KEY (cfk_...){RESET}\n")
        raise SystemExit(1)

    info_url = f"{base_url}/v1/account/info"
    masked_key = api_key[:8] + "..." + api_key[-4:] if len(api_key) > 12 else api_key

    print(f"\n{CYAN}{BOLD}  Validating CacheForge connection...{RESET}")
    print(f"{DIM}  GET {info_url}{RESET}")
    print(f"{DIM}  Key: {masked_key}{RESET}\n")

    result = http_get(info_url, headers={"Authorization": f"Bearer {api_key}"})

    # Handle HTTP errors
    http_error = result.get("_http_error")
    if http_error:
        body = result.get("_body", "")
        if http_error == 401:
            print(f"{RED}  Authentication failed (401).{RESET}")
            print(f"{YELLOW}  Your API key is invalid or expired.{RESET}")
            print(f"{DIM}  Run 'provision' to get a new key, or check CACHEFORGE_API_KEY.{RESET}\n")
            raise SystemExit(1)
        elif http_error == 402:
            print(f"{YELLOW}  Payment required (402).{RESET}")
            print(f"{YELLOW}  Your account is active but has no credits remaining.{RESET}")
            print(f"{DIM}  Visit {base_url} to add credits or upgrade your plan.{RESET}\n")
            raise SystemExit(1)
        else:
            print(f"{RED}  Unexpected error ({http_error}).{RESET}")
            print(f"{DIM}  {body[:500]}{RESET}\n")
            raise SystemExit(1)

    # Success — display account info
    # API returns {"tenant": {"id": "...", "name": "...", "status": "...", ...}}
    tenant_data = result.get("tenant", {})
    if isinstance(tenant_data, dict):
        tenant_name = tenant_data.get("name", "unknown")
        status = tenant_data.get("status", "active")
        upstream_ok = tenant_data.get("upstreamConfigured", False)
    else:
        tenant_name = str(tenant_data) if tenant_data else "unknown"
        status = "active"
        upstream_ok = False

    info_lines = [("Status", f"{status}")]
    if tenant_name:
        info_lines.insert(0, ("Tenant", tenant_name))
    if upstream_ok:
        info_lines.append(("Upstream", "configured"))
    info_lines.append(("Endpoint", f"{base_url}/v1"))

    print(draw_box("Connection OK", info_lines, color=CYAN))
    print(f"\n{GREEN}  CacheForge is working. All requests will be proxied and optimized.{RESET}\n")


# ── CLI entrypoint ───────────────────────────────────────────────────────────


def main() -> None:
    parser = argparse.ArgumentParser(
        description="CacheForge setup CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Examples:\n"
            "  python setup.py provision --email me@co.com --password s3cret --upstream-key sk-or-...\n"
            "  python setup.py validate --api-key cfk_abc123\n"
        ),
    )
    sub = parser.add_subparsers(dest="command", required=True)

    # ── provision ──
    prov = sub.add_parser("provision", help="Register/authenticate and get a CacheForge API key")
    prov.add_argument("--email", help="Account email address")
    prov.add_argument("--password", help="Account password")
    prov.add_argument("--invite-code", help="Invite code (required on invite-only deployments)")
    prov.add_argument("--upstream-kind", choices=["openai", "openrouter", "anthropic"],
                      help="Upstream LLM provider (auto-detected from key prefix)")
    prov.add_argument("--upstream-key", help="Upstream provider API key")
    prov.add_argument("--base-url", help=f"CacheForge base URL (default: {DEFAULT_BASE_URL})")

    # ── validate ──
    val = sub.add_parser("validate", help="Validate an existing CacheForge setup")
    val.add_argument("--api-key", help="CacheForge API key (cfk_...)")
    val.add_argument("--base-url", help=f"CacheForge base URL (default: {DEFAULT_BASE_URL})")

    args = parser.parse_args()

    if args.command == "provision":
        cmd_provision(args)
    elif args.command == "validate":
        cmd_validate(args)


if __name__ == "__main__":
    main()
