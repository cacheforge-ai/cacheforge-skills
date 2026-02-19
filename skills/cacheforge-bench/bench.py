#!/usr/bin/env python3
"""CacheForge Benchmark Runner -- LLM cost benchmarks with and without CacheForge.

Stdlib-only (no external deps). Measures tokens, latency, and cost across
providers. Renders rich terminal reports with Unicode box drawing and ANSI
colours.

Part of the CacheForge toolkit — https://app.anvil-ai.io
"""

import argparse
import json
import os
import re
import shutil
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone

# ---------------------------------------------------------------------------
# ANSI colour helpers
# ---------------------------------------------------------------------------

RESET = "\033[0m"
BOLD = "\033[1m"
DIM = "\033[2m"
RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
CYAN = "\033[96m"
WHITE = "\033[97m"
MAGENTA = "\033[95m"

NO_COLOR = os.environ.get("NO_COLOR") is not None or not sys.stdout.isatty()


def c(text: str, *codes: str) -> str:
    """Wrap *text* in ANSI colour escape sequences (respects NO_COLOR)."""
    if NO_COLOR:
        return str(text)
    return "".join(codes) + str(text) + RESET


def strip_ansi(s: str) -> str:
    """Remove ANSI escape codes for length calculations."""
    return re.sub(r"\033\[[0-9;]*m", "", s)


# ---------------------------------------------------------------------------
# Formatting helpers
# ---------------------------------------------------------------------------

def format_tokens(n: int) -> str:
    if n >= 1_000_000:
        return f"{n / 1_000_000:.1f}M"
    if n >= 1_000:
        return f"{n / 1_000:.1f}K"
    return str(n)


def format_usd(amount: float) -> str:
    if amount < 0.01:
        return f"${amount:.4f}"
    return f"${amount:,.2f}"


def format_ms(ms: float) -> str:
    if ms >= 1000:
        return f"{ms / 1000:.2f}s"
    return f"{ms:.0f}ms"


def bar(value: float, max_val: float, width: int = 30) -> str:
    if max_val <= 0:
        filled = 0
    else:
        filled = int(round((value / max_val) * width))
        filled = max(0, min(filled, width))
    empty = width - filled
    return c("\u2588" * filled, GREEN) + c("\u2591" * empty, WHITE)


def pct_bar(pct: float, width: int = 30) -> str:
    return bar(pct, 100, width)


def savings_bar(pct: float, width: int = 30) -> str:
    if pct <= 0:
        filled = 0
    else:
        filled = int(round((pct / 100.0) * width))
        filled = max(0, min(filled, width))
    empty = width - filled
    if pct >= 20:
        clr = GREEN
    elif pct >= 10:
        clr = YELLOW
    else:
        clr = RED
    return c("\u2588" * filled, clr) + c("\u2591" * empty, DIM)


# ---------------------------------------------------------------------------
# Terminal width
# ---------------------------------------------------------------------------

def term_width(default: int = 80) -> int:
    try:
        cols = shutil.get_terminal_size((default, 24)).columns
    except Exception:
        cols = default
    return max(cols, 50)


# ---------------------------------------------------------------------------
# Box-drawing helpers
# ---------------------------------------------------------------------------

def box_top(w: int) -> str:
    return "\u250c" + "\u2500" * (w - 2) + "\u2510"


def box_mid(w: int) -> str:
    return "\u251c" + "\u2500" * (w - 2) + "\u2524"


def box_bot(w: int) -> str:
    return "\u2514" + "\u2500" * (w - 2) + "\u2518"


def box_row(text: str, w: int) -> str:
    visible_len = len(strip_ansi(text))
    inner = w - 4  # 4 = "│ " + " │"
    pad = max(inner - visible_len, 0)
    if visible_len <= inner:
        return "\u2502 " + text + " " * pad + " \u2502"
    return "\u2502 " + strip_ansi(text)[:inner] + " \u2502"


def box_empty(w: int) -> str:
    return box_row("", w)


# ---------------------------------------------------------------------------
# Provider pricing (approximate $/1M tokens for cost estimates)
# ---------------------------------------------------------------------------

PRICING = {
    "gpt-4o": {"input": 2.50, "output": 10.00},
    "gpt-4o-mini": {"input": 0.15, "output": 0.60},
    "gpt-4-turbo": {"input": 10.00, "output": 30.00},
    "gpt-3.5-turbo": {"input": 0.50, "output": 1.50},
    "claude-sonnet-4-6": {"input": 3.00, "output": 15.00},
    "claude-haiku-4-5-20251001": {"input": 0.80, "output": 4.00},
    "claude-3-5-sonnet-20241022": {"input": 3.00, "output": 15.00},
    "claude-3-haiku-20240307": {"input": 0.25, "output": 1.25},
}

DEFAULT_PRICING = {"input": 3.00, "output": 15.00}

PROVIDER_URLS = {
    "openai": "https://api.openai.com/v1",
    "openrouter": "https://openrouter.ai/api/v1",
}

PROVIDER_KEY_ENVS = {
    "openai": "OPENAI_API_KEY",
    "openrouter": "OPENROUTER_API_KEY",
}


def get_pricing(model: str) -> dict:
    for key, val in PRICING.items():
        if key in model.lower():
            return val
    return DEFAULT_PRICING


def estimate_cost(model: str, prompt_tokens: int, completion_tokens: int) -> float:
    p = get_pricing(model)
    return (prompt_tokens * p["input"] + completion_tokens * p["output"]) / 1_000_000


# ---------------------------------------------------------------------------
# Built-in benchmark prompt suite
# ---------------------------------------------------------------------------

_HEAVY_TOOL_SCHEMA = [
    {"type": "function", "function": {"name": "web_fetch", "description": "Fetch and extract readable content from a URL (HTML to markdown/text). Use for lightweight page access without browser automation.", "parameters": {"type": "object", "properties": {"url": {"type": "string", "description": "HTTP or HTTPS URL to fetch."}, "extractMode": {"type": "string", "enum": ["markdown", "text"], "description": "Extraction mode."}, "maxChars": {"type": "number", "description": "Maximum characters to return."}}, "required": ["url"]}}},
    {"type": "function", "function": {"name": "browser_snapshot", "description": "Take a snapshot of the current browser page. Returns accessibility tree with interactive element references for automation.", "parameters": {"type": "object", "properties": {"action": {"type": "string", "enum": ["snapshot", "screenshot", "navigate", "act"]}, "url": {"type": "string"}, "selector": {"type": "string"}, "ref": {"type": "string"}, "compact": {"type": "boolean"}, "fullPage": {"type": "boolean"}}, "required": ["action"]}}},
    {"type": "function", "function": {"name": "browser_act", "description": "Perform an action on the browser page: click, type, press, hover, drag, select, fill, resize, wait, evaluate, close.", "parameters": {"type": "object", "properties": {"action": {"type": "string", "enum": ["act"]}, "request": {"type": "object", "properties": {"kind": {"type": "string", "enum": ["click", "type", "press", "hover", "drag", "select", "fill", "resize", "wait", "evaluate", "close"]}, "ref": {"type": "string"}, "text": {"type": "string"}, "key": {"type": "string"}, "modifiers": {"type": "array", "items": {"type": "string"}}, "submit": {"type": "boolean"}, "slowly": {"type": "boolean"}, "timeMs": {"type": "number"}, "textGone": {"type": "string"}}, "required": ["kind"]}}, "required": ["action", "request"]}}},
    {"type": "function", "function": {"name": "exec_command", "description": "Execute shell commands with background continuation. Use for running scripts, builds, tests, and system operations.", "parameters": {"type": "object", "properties": {"command": {"type": "string", "description": "Shell command to execute."}, "workdir": {"type": "string"}, "timeout": {"type": "number"}, "background": {"type": "boolean"}, "pty": {"type": "boolean"}}, "required": ["command"]}}},
    {"type": "function", "function": {"name": "read_file", "description": "Read the contents of a file. Supports text files and images.", "parameters": {"type": "object", "properties": {"path": {"type": "string"}, "offset": {"type": "number"}, "limit": {"type": "number"}}, "required": ["path"]}}},
    {"type": "function", "function": {"name": "write_file", "description": "Write content to a file. Creates parent directories automatically.", "parameters": {"type": "object", "properties": {"path": {"type": "string"}, "content": {"type": "string"}}, "required": ["path", "content"]}}},
    {"type": "function", "function": {"name": "edit_file", "description": "Edit a file by replacing exact text. The old text must match exactly including whitespace.", "parameters": {"type": "object", "properties": {"path": {"type": "string"}, "old_string": {"type": "string"}, "new_string": {"type": "string"}}, "required": ["path", "old_string", "new_string"]}}},
    {"type": "function", "function": {"name": "search_code", "description": "Search across files using ripgrep. Returns matching lines with file paths and line numbers.", "parameters": {"type": "object", "properties": {"pattern": {"type": "string"}, "path": {"type": "string"}, "include": {"type": "string"}, "context": {"type": "number"}}, "required": ["pattern"]}}},
    {"type": "function", "function": {"name": "memory_search", "description": "Semantically search memory files. Returns top matching snippets with file paths and line numbers.", "parameters": {"type": "object", "properties": {"query": {"type": "string"}, "maxResults": {"type": "number"}, "minScore": {"type": "number"}}, "required": ["query"]}}},
    {"type": "function", "function": {"name": "web_search", "description": "Search the web using Brave Search API. Returns titles, URLs, and snippets.", "parameters": {"type": "object", "properties": {"query": {"type": "string"}, "count": {"type": "number", "minimum": 1, "maximum": 10}, "country": {"type": "string"}, "freshness": {"type": "string"}}, "required": ["query"]}}},
]

_FAKE_HTML_BODY = """<!DOCTYPE html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Dashboard - Analytics Platform</title><link rel="stylesheet" href="/assets/css/main.css"><script src="/assets/js/analytics.js" defer></script></head><body><nav class="navbar navbar-expand-lg navbar-dark bg-primary"><div class="container-fluid"><a class="navbar-brand" href="/">AnalyticsPro</a><div class="collapse navbar-collapse"><ul class="navbar-nav me-auto"><li class="nav-item"><a class="nav-link active" href="/dashboard">Dashboard</a></li><li class="nav-item"><a class="nav-link" href="/reports">Reports</a></li><li class="nav-item dropdown"><a class="nav-link dropdown-toggle" href="#" data-bs-toggle="dropdown">Settings</a><ul class="dropdown-menu"><li><a class="dropdown-item" href="/settings/profile">Profile</a></li><li><a class="dropdown-item" href="/settings/billing">Billing</a></li><li><a class="dropdown-item" href="/settings/api-keys">API Keys</a></li><li><hr class="dropdown-divider"></li><li><a class="dropdown-item" href="/settings/team">Team Management</a></li></ul></li></ul><div class="d-flex align-items-center"><span class="badge bg-success me-3">Pro Plan</span><img src="/avatar.jpg" class="rounded-circle" width="32" alt="User"></div></div></div></nav><main class="container-fluid mt-4"><div class="row"><div class="col-xl-3 col-md-6 mb-4"><div class="card border-left-primary shadow h-100 py-2"><div class="card-body"><div class="row no-gutters align-items-center"><div class="col mr-2"><div class="text-xs font-weight-bold text-primary text-uppercase mb-1">Monthly Revenue</div><div class="h5 mb-0 font-weight-bold text-gray-800">$42,847.92</div><div class="text-xs text-success mt-1">+12.5% from last month</div></div><div class="col-auto"><i class="fas fa-dollar-sign fa-2x text-gray-300"></i></div></div></div></div></div><div class="col-xl-3 col-md-6 mb-4"><div class="card border-left-success shadow h-100 py-2"><div class="card-body"><div class="row no-gutters align-items-center"><div class="col mr-2"><div class="text-xs font-weight-bold text-success text-uppercase mb-1">Active Users</div><div class="h5 mb-0 font-weight-bold text-gray-800">2,847</div><div class="text-xs text-success mt-1">+8.3% from last month</div></div></div></div></div></div><div class="col-xl-3 col-md-6 mb-4"><div class="card border-left-info shadow h-100 py-2"><div class="card-body"><div class="row no-gutters align-items-center"><div class="col mr-2"><div class="text-xs font-weight-bold text-info text-uppercase mb-1">API Requests (24h)</div><div class="h5 mb-0 font-weight-bold text-gray-800">1,284,937</div></div></div></div></div></div></div><div class="row"><div class="col-lg-8"><div class="card shadow mb-4"><div class="card-header py-3 d-flex flex-row align-items-center justify-content-between"><h6 class="m-0 font-weight-bold text-primary">Revenue Overview</h6></div><div class="card-body"><canvas id="revenueChart"></canvas><table class="table table-striped mt-3"><thead><tr><th>Date</th><th>Transactions</th><th>Revenue</th><th>Avg Order</th><th>Conversion Rate</th></tr></thead><tbody><tr><td>2026-02-18</td><td>1,247</td><td>$8,432.10</td><td>$6.76</td><td>3.2%</td></tr><tr><td>2026-02-17</td><td>1,189</td><td>$7,891.45</td><td>$6.64</td><td>3.1%</td></tr><tr><td>2026-02-16</td><td>1,302</td><td>$9,104.22</td><td>$6.99</td><td>3.4%</td></tr><tr><td>2026-02-15</td><td>987</td><td>$6,234.87</td><td>$6.32</td><td>2.8%</td></tr><tr><td>2026-02-14</td><td>1,456</td><td>$11,234.56</td><td>$7.71</td><td>3.9%</td></tr></tbody></table></div></div></div><div class="col-lg-4"><div class="card shadow mb-4"><div class="card-header py-3"><h6 class="m-0 font-weight-bold text-primary">Traffic Sources</h6></div><div class="card-body"><div class="chart-pie"><canvas id="trafficChart"></canvas></div><div class="mt-4"><div class="d-flex justify-content-between"><span>Direct</span><span>42.3%</span></div><div class="progress mb-2"><div class="progress-bar bg-primary" style="width:42.3%"></div></div><div class="d-flex justify-content-between"><span>Organic Search</span><span>28.7%</span></div><div class="progress mb-2"><div class="progress-bar bg-success" style="width:28.7%"></div></div><div class="d-flex justify-content-between"><span>Referral</span><span>18.2%</span></div><div class="progress mb-2"><div class="progress-bar bg-info" style="width:18.2%"></div></div><div class="d-flex justify-content-between"><span>Social</span><span>10.8%</span></div><div class="progress mb-2"><div class="progress-bar bg-warning" style="width:10.8%"></div></div></div></div></div></div></div></main><footer class="footer mt-auto py-3 bg-light"><div class="container text-center text-muted">AnalyticsPro Dashboard v3.2.1 &copy; 2026</div></footer></body></html>"""

_FAKE_API_RESPONSE = json.dumps({
    "data": {
        "users": [
            {"id": f"usr_{i:04d}", "email": f"user{i}@example.com", "name": f"User {i}",
             "role": "admin" if i < 3 else "member", "status": "active",
             "created_at": f"2026-01-{(i % 28) + 1:02d}T10:00:00Z",
             "last_login": f"2026-02-{(i % 19) + 1:02d}T{8 + i % 12}:00:00Z",
             "metadata": {"plan": "pro" if i < 5 else "free", "tokens_used": 10000 + i * 2500,
                          "tokens_limit": 100000, "features": ["api", "dashboard", "export"] if i < 5 else ["api"],
                          "billing": {"method": "stripe", "customer_id": f"cus_{i * 1111:08x}",
                                      "subscription_id": f"sub_{i * 2222:08x}"}}}
            for i in range(20)
        ],
        "pagination": {"page": 1, "per_page": 20, "total": 847, "total_pages": 43},
        "aggregations": {
            "by_plan": {"pro": 142, "free": 705},
            "by_status": {"active": 798, "suspended": 31, "pending": 18},
            "by_role": {"admin": 12, "member": 835},
        }
    },
    "meta": {"request_id": "req_abc123", "processing_time_ms": 47, "cache_hit": False},
}, indent=2)

_FAKE_BROWSER_SNAPSHOT = """role: WebArea, name: "GitHub - cacheforge-ai/cacheforge-skills"
  role: banner
    role: navigation, name: "Global"
      role: link, name: "Homepage", ref: e1
      role: search, name: "Search or jump to..."
        role: textbox, name: "Search", ref: e2
      role: list
        role: listitem
          role: link, name: "Pull requests", ref: e3
        role: listitem
          role: link, name: "Issues", ref: e4
        role: listitem
          role: link, name: "Marketplace", ref: e5
        role: listitem
          role: link, name: "Explore", ref: e6
  role: main
    role: heading, name: "cacheforge-ai/cacheforge-skills", level: 1
      role: link, name: "cacheforge-ai", ref: e7
      role: link, name: "cacheforge-skills", ref: e8
    role: navigation, name: "Repository"
      role: link, name: "Code", ref: e9
      role: link, name: "Issues 0", ref: e10
      role: link, name: "Pull requests 3", ref: e11
      role: link, name: "Actions", ref: e12
      role: link, name: "Security", ref: e13
      role: link, name: "Insights", ref: e14
    role: group, name: "Repository stats"
      role: link, name: "6 stars", ref: e15
      role: link, name: "2 forks", ref: e16
      role: link, name: "MIT license", ref: e17
    role: article, name: "README"
      role: heading, name: "CacheForge — Agent Skills", level: 1
      role: paragraph, text: "Cut your agent's token bill by up to 30% or more. CacheForge is a drop-in optimization layer that sits between your agent and your LLM provider."
      role: heading, name: "Skills", level: 2
      role: table
        role: row
          role: cell, text: "cacheforge"
          role: cell, text: "Connect any OpenAI-compatible agent to CacheForge"
        role: row
          role: cell, text: "cacheforge-setup"
          role: cell, text: "Guided onboarding — register, configure upstream"
        role: row
          role: cell, text: "cacheforge-ops"
          role: cell, text: "Account operations — balance, top up, API keys"
        role: row
          role: cell, text: "cacheforge-stats"
          role: cell, text: "Terminal dashboard — usage, savings, breakdown"
        role: row
          role: cell, text: "cacheforge-bench"
          role: cell, text: "LLM cost benchmark runner"
        role: row
          role: cell, text: "context-engineer"
          role: cell, text: "Context window optimizer"
        role: row
          role: cell, text: "agentic-devops"
          role: cell, text: "Production-grade DevOps toolkit"
    role: complementary, name: "About"
      role: paragraph, text: "Agent Skills for CacheForge — enterprise-grade LLM optimization"
      role: list, name: "Topics"
        role: listitem
          role: link, name: "ai-agents", ref: e18
        role: listitem
          role: link, name: "llm", ref: e19
        role: listitem
          role: link, name: "token-optimization", ref: e20
    role: navigation, name: "File list"
      role: table
        role: row
          role: cell, text: "skills/"
          role: cell, text: "feat: add agentic-devops skill"
          role: cell, text: "2 hours ago"
        role: row
          role: cell, text: "README.md"
          role: cell, text: "merge: resolve README conflict"
          role: cell, text: "2 hours ago"
"""

BUILTIN_PROMPTS = [
    {
        "name": "Browser Snapshot Analysis",
        "description": "Heavy accessibility tree — typical browser-use payload",
        "messages": [
            {
                "role": "system",
                "content": "You are a web automation assistant. You control a browser via snapshots of the accessibility tree. Each element has a ref you can use to interact with it.",
            },
            {
                "role": "user",
                "content": "I need to navigate to the CacheForge skills repo and star it. Here's the current browser snapshot:\n\n" + _FAKE_BROWSER_SNAPSHOT + "\n\nWhat element should I click to star the repo?",
            },
        ],
    },
    {
        "name": "HTML Page Processing",
        "description": "Large HTML payload — web scraping / extraction workload",
        "messages": [
            {
                "role": "system",
                "content": "You are a data extraction assistant. Parse HTML pages and extract structured data.",
            },
            {
                "role": "user",
                "content": "Extract the key metrics from this analytics dashboard HTML and summarize the business performance:\n\n" + _FAKE_HTML_BODY,
            },
        ],
    },
    {
        "name": "JSON API Response Analysis",
        "description": "Large structured JSON — typical API integration payload",
        "messages": [
            {
                "role": "system",
                "content": "You are a data analyst assistant. Analyze API responses and provide insights.",
            },
            {
                "role": "user",
                "content": "Analyze this user management API response and give me a summary of user distribution, plan adoption, and any concerns:\n\n```json\n" + _FAKE_API_RESPONSE + "\n```",
            },
        ],
    },
    {
        "name": "Heavy Tool Schema",
        "description": "10 tool definitions — agent framework overhead",
        "messages": [
            {
                "role": "system",
                "content": "You are a capable AI assistant with access to browser, file, search, and web tools. Use the most appropriate tool for each task.",
            },
            {
                "role": "user",
                "content": "Search for the latest CacheForge release notes, then navigate to the GitHub repo and check if there are any open issues.",
            },
        ],
        "tools": _HEAVY_TOOL_SCHEMA,
    },
    {
        "name": "Multi-Turn with Tool Results",
        "description": "Accumulated context — conversation with prior tool outputs and HTML",
        "messages": [
            {
                "role": "system",
                "content": "You are a web research assistant with browser and fetch capabilities. You help users research products, compare pricing, and make informed decisions.",
            },
            {"role": "user", "content": "Find me the latest pricing for OpenAI's API and compare it to Anthropic."},
            {"role": "assistant", "content": "I'll fetch both pricing pages for you."},
            {
                "role": "user",
                "content": "Here's what web_fetch returned for OpenAI:\n\n" + json.dumps({
                    "url": "https://openai.com/api/pricing",
                    "status": 200,
                    "content": "# API Pricing\n\n## GPT-4o\n- Input: $2.50 / 1M tokens\n- Cached input: $1.25 / 1M tokens\n- Output: $10.00 / 1M tokens\n\n## GPT-4o mini\n- Input: $0.150 / 1M tokens\n- Cached input: $0.075 / 1M tokens\n- Output: $0.600 / 1M tokens\n\n## GPT-4 Turbo\n- Input: $10.00 / 1M tokens\n- Output: $30.00 / 1M tokens\n\n## o1\n- Input: $15.00 / 1M tokens\n- Cached input: $7.50 / 1M tokens\n- Output: $60.00 / 1M tokens\n\n## o1-mini\n- Input: $1.10 / 1M tokens\n- Cached input: $0.55 / 1M tokens\n- Output: $4.40 / 1M tokens\n\n## Embedding Models\n- text-embedding-3-small: $0.020 / 1M tokens\n- text-embedding-3-large: $0.130 / 1M tokens\n\n## Image Models\n- DALL-E 3 HD: $0.080 / image\n- DALL-E 3: $0.040 / image\n- gpt-image-1 HD: $0.080 / image\n\n## Audio Models\n- Whisper: $0.006 / minute\n- TTS: $0.015 / 1K chars\n- TTS HD: $0.030 / 1K chars",
                    "fetchedAt": "2026-02-19T12:00:00Z",
                }, indent=2) + "\n\nAnd here's Anthropic:\n\n" + json.dumps({
                    "url": "https://docs.anthropic.com/en/docs/about-claude/models",
                    "status": 200,
                    "content": "# Model Pricing\n\n## Claude Opus 4\n- Input: $15.00 / 1M tokens\n- Output: $75.00 / 1M tokens\n- Prompt caching write: $18.75 / 1M tokens\n- Prompt caching read: $1.50 / 1M tokens\n\n## Claude Sonnet 4\n- Input: $3.00 / 1M tokens\n- Output: $15.00 / 1M tokens\n- Prompt caching write: $3.75 / 1M tokens\n- Prompt caching read: $0.30 / 1M tokens\n\n## Claude Haiku 3.5\n- Input: $0.80 / 1M tokens\n- Output: $4.00 / 1M tokens\n- Prompt caching write: $1.00 / 1M tokens\n- Prompt caching read: $0.08 / 1M tokens\n\n## Context Windows\n- Opus 4: 200K (1M beta)\n- Sonnet 4: 200K (1M beta)\n- Haiku 3.5: 200K",
                    "fetchedAt": "2026-02-19T12:00:00Z",
                }, indent=2) + "\n\nI'm spending about $500/month across both providers. Build me a comparison table and estimate what CacheForge would save me on each.",
            },
        ],
    },
    {
        "name": "Repeated Heavy Context",
        "description": "Same browser snapshot, new question — cache-hit potential",
        "messages": [
            {
                "role": "system",
                "content": "You are a web automation assistant. You control a browser via snapshots of the accessibility tree. Each element has a ref you can use to interact with it.",
            },
            {
                "role": "user",
                "content": "Here's the current page snapshot:\n\n" + _FAKE_BROWSER_SNAPSHOT + "\n\nHow many open pull requests does this repo have, and what ref would I click to see them?",
            },
        ],
    },
]


# ---------------------------------------------------------------------------
# HTTP helpers
# ---------------------------------------------------------------------------

def _openai_chat(base_url: str, api_key: str, model: str,
                 messages: list, max_tokens: int = 256,
                 tools=None) -> dict:
    """Send a chat completion request (OpenAI-compatible API)."""
    url = f"{base_url.rstrip('/')}/chat/completions"
    body = {
        "model": model,
        "messages": messages,
        "max_tokens": max_tokens,
    }
    if tools:
        body["tools"] = tools
    payload = json.dumps(body).encode()

    req = urllib.request.Request(url, data=payload, headers={
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    })

    start = time.monotonic()
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            latency_ms = (time.monotonic() - start) * 1000
            body = json.loads(resp.read().decode())
            usage = body.get("usage", {})
            return {
                "ok": True,
                "latency_ms": latency_ms,
                "prompt_tokens": usage.get("prompt_tokens", 0),
                "completion_tokens": usage.get("completion_tokens", 0),
                "total_tokens": usage.get("total_tokens", 0),
                "model": body.get("model", model),
            }
    except urllib.error.HTTPError as exc:
        latency_ms = (time.monotonic() - start) * 1000
        try:
            err_body = exc.read().decode()
        except Exception:
            err_body = str(exc)
        return {
            "ok": False,
            "latency_ms": latency_ms,
            "error": f"HTTP {exc.code}: {err_body[:200]}",
            "prompt_tokens": 0,
            "completion_tokens": 0,
            "total_tokens": 0,
            "model": model,
        }
    except urllib.error.URLError as exc:
        latency_ms = (time.monotonic() - start) * 1000
        return {
            "ok": False,
            "latency_ms": latency_ms,
            "error": f"Connection error: {exc.reason}",
            "prompt_tokens": 0,
            "completion_tokens": 0,
            "total_tokens": 0,
            "model": model,
        }


# ---------------------------------------------------------------------------
# Load custom prompts
# ---------------------------------------------------------------------------

def load_custom_prompts(path: str) -> list:
    """Load prompts from a JSON file. Expected format: list of objects with
    'name', 'messages', and optional 'description'."""
    with open(path, "r") as f:
        data = json.load(f)
    if not isinstance(data, list):
        print(c(f"Error: {path} must contain a JSON array of prompt objects.", RED),
              file=sys.stderr)
        sys.exit(1)
    prompts = []
    for i, item in enumerate(data):
        if not isinstance(item, dict) or "messages" not in item:
            print(c(f"Error: prompt #{i} missing 'messages' field.", RED),
                  file=sys.stderr)
            sys.exit(1)
        prompts.append({
            "name": item.get("name", f"Custom #{i + 1}"),
            "description": item.get("description", "User-provided prompt"),
            "messages": item["messages"],
            "tools": item.get("tools"),
        })
    return prompts


def make_inline_prompt(text: str) -> list:
    """Create a single-prompt suite from inline text."""
    return [{
        "name": "Inline Prompt",
        "description": "User-provided inline prompt",
        "messages": [{"role": "user", "content": text}],
    }]


# ---------------------------------------------------------------------------
# Benchmark runner
# ---------------------------------------------------------------------------

def run_benchmark(base_url: str, api_key: str, model: str,
                  prompts: list, label: str = "benchmark",
                  max_tokens: int = 256) -> dict:
    """Run the benchmark suite and return a results dict."""
    results = []
    total_prompt = 0
    total_completion = 0
    total_latency = 0.0
    errors = 0

    w = min(term_width(), 80)
    print()
    print(c(f"  Running {label}...", CYAN, BOLD))
    print(c(f"  Endpoint: {base_url}", DIM))
    print(c(f"  Model:    {model}", DIM))
    print(c(f"  Prompts:  {len(prompts)}", DIM))
    print()

    for i, prompt in enumerate(prompts):
        name = prompt["name"]
        sys.stdout.write(c(f"  [{i + 1}/{len(prompts)}] {name:<30s}", WHITE))
        sys.stdout.flush()

        resp = _openai_chat(base_url, api_key, model,
                            prompt["messages"], max_tokens,
                            tools=prompt.get("tools"))

        if resp["ok"]:
            cost = estimate_cost(model, resp["prompt_tokens"],
                                 resp["completion_tokens"])
            sys.stdout.write(
                c(f" {format_ms(resp['latency_ms']):>8s}", GREEN)
                + c(f"  {resp['prompt_tokens']:>6d}+{resp['completion_tokens']:<5d} tok", DIM)
                + c(f"  {format_usd(cost)}", GREEN)
                + "\n"
            )
        else:
            errors += 1
            sys.stdout.write(c(f"  FAILED: {resp['error'][:50]}", RED) + "\n")

        result_entry = {
            "name": name,
            "description": prompt.get("description", ""),
            "ok": resp["ok"],
            "latency_ms": resp["latency_ms"],
            "prompt_tokens": resp["prompt_tokens"],
            "completion_tokens": resp["completion_tokens"],
            "total_tokens": resp["total_tokens"],
            "estimated_cost_usd": estimate_cost(
                model, resp["prompt_tokens"], resp["completion_tokens"]
            ) if resp["ok"] else 0,
        }
        if not resp["ok"]:
            result_entry["error"] = resp.get("error", "Unknown error")

        results.append(result_entry)
        total_prompt += resp["prompt_tokens"]
        total_completion += resp["completion_tokens"]
        total_latency += resp["latency_ms"]

    total_cost = estimate_cost(model, total_prompt, total_completion)

    return {
        "label": label,
        "endpoint": base_url,
        "model": model,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "prompts_run": len(prompts),
        "errors": errors,
        "total_prompt_tokens": total_prompt,
        "total_completion_tokens": total_completion,
        "total_tokens": total_prompt + total_completion,
        "total_latency_ms": total_latency,
        "avg_latency_ms": total_latency / len(prompts) if prompts else 0,
        "estimated_total_cost_usd": total_cost,
        "results": results,
    }


# ---------------------------------------------------------------------------
# Report rendering
# ---------------------------------------------------------------------------

def render_single_report(data: dict) -> None:
    """Render a terminal report for a single benchmark run."""
    w = min(term_width(), 80)
    lines = []

    lines.append(box_top(w))
    title = c("  CacheForge Benchmark Results", CYAN, BOLD)
    lines.append(box_row(title, w))
    lines.append(box_row(c(f"  {data.get('timestamp', '')[:19]}", DIM), w))
    lines.append(box_mid(w))

    # Summary
    lines.append(box_row(c("  Summary", CYAN), w))
    lines.append(box_row("  " + "\u2500" * (w - 6), w))

    model = data.get("model", "unknown")
    endpoint = data.get("endpoint", "unknown")
    lines.append(box_row(f"  Model:         {c(model, WHITE)}", w))
    lines.append(box_row(f"  Endpoint:      {c(endpoint, DIM)}", w))
    lines.append(box_row(
        f"  Prompts:       {data.get('prompts_run', 0)}"
        f"    Errors: {c(str(data.get('errors', 0)), RED if data.get('errors', 0) > 0 else GREEN)}",
        w,
    ))
    lines.append(box_empty(w))

    total_tok = data.get("total_tokens", 0)
    prompt_tok = data.get("total_prompt_tokens", 0)
    comp_tok = data.get("total_completion_tokens", 0)
    avg_lat = data.get("avg_latency_ms", 0)
    total_cost = data.get("estimated_total_cost_usd", 0)

    lines.append(box_row(
        f"  Total Tokens:  {c(format_tokens(total_tok), WHITE)}"
        f"  (prompt: {format_tokens(prompt_tok)}, completion: {format_tokens(comp_tok)})",
        w,
    ))
    lines.append(box_row(
        f"  Avg Latency:   {c(format_ms(avg_lat), WHITE)}"
        f"    Est. Cost: {c(format_usd(total_cost), GREEN)}",
        w,
    ))

    lines.append(box_mid(w))

    # Per-prompt results
    lines.append(box_row(c("  Per-Prompt Results", CYAN), w))
    lines.append(box_row("  " + "\u2500" * (w - 6), w))

    results = data.get("results", [])
    max_lat = max((r.get("latency_ms", 0) for r in results), default=1)
    bar_w = max(w - 55, 8)

    for r in results:
        name = r.get("name", "?")[:22]
        lat = r.get("latency_ms", 0)
        ok = r.get("ok", False)
        if ok:
            cost = r.get("estimated_cost_usd", 0)
            lat_bar = bar(lat, max_lat, bar_w)
            lines.append(box_row(
                f"  {name:<22s} {lat_bar} {format_ms(lat):>7s}  {format_usd(cost):>8s}",
                w,
            ))
        else:
            lines.append(box_row(
                f"  {name:<22s} {c('FAILED', RED)}",
                w,
            ))

    lines.append(box_bot(w))
    print("\n".join(lines))


def render_comparison_report(direct: dict, cacheforge: dict) -> None:
    """Render a side-by-side comparison report."""
    w = min(term_width(), 80)
    lines = []

    lines.append(box_top(w))
    title = c("  CacheForge A/B Comparison", CYAN, BOLD)
    lines.append(box_row(title, w))
    lines.append(box_row(c(f"  {direct.get('timestamp', '')[:19]}", DIM), w))
    lines.append(box_mid(w))

    # Endpoints
    lines.append(box_row(c("  Endpoints", CYAN), w))
    lines.append(box_row("  " + "\u2500" * (w - 6), w))
    lines.append(box_row(f"  Direct:     {c(direct.get('endpoint', ''), DIM)}", w))
    lines.append(box_row(f"  CacheForge: {c(cacheforge.get('endpoint', ''), DIM)}", w))
    lines.append(box_row(f"  Model:      {c(direct.get('model', ''), WHITE)}", w))
    lines.append(box_mid(w))

    # Overall comparison
    lines.append(box_row(c("  Overall Comparison", CYAN), w))
    lines.append(box_row("  " + "\u2500" * (w - 6), w))

    d_tokens = direct.get("total_tokens", 0)
    cf_tokens = cacheforge.get("total_tokens", 0)
    d_cost = direct.get("estimated_total_cost_usd", 0)
    cf_cost = cacheforge.get("estimated_total_cost_usd", 0)
    d_lat = direct.get("avg_latency_ms", 0)
    cf_lat = cacheforge.get("avg_latency_ms", 0)

    token_saved = d_tokens - cf_tokens
    token_pct = (token_saved / d_tokens * 100) if d_tokens > 0 else 0
    cost_saved = d_cost - cf_cost
    cost_pct = (cost_saved / d_cost * 100) if d_cost > 0 else 0
    latency_diff = d_lat - cf_lat
    latency_pct = (latency_diff / d_lat * 100) if d_lat > 0 else 0

    bar_w = max(w - 40, 10)

    def comparison_row(label, d_val, cf_val, fmt_fn, saved, pct):
        lines.append(box_row(f"  {label}", w))
        lines.append(box_row(
            f"    Direct:     {fmt_fn(d_val):>12s}"
            f"    CacheForge: {c(fmt_fn(cf_val), GREEN):>12s}",
            w,
        ))
        if pct > 0:
            lines.append(box_row(
                f"    Saved:      {c(fmt_fn(saved), GREEN):>12s}"
                f"    ({c(f'{pct:.1f}%', GREEN)})",
                w,
            ))
        elif pct < 0:
            lines.append(box_row(
                f"    Delta:      {c(fmt_fn(abs(saved)), YELLOW):>12s}"
                f"    ({c(f'+{abs(pct):.1f}%', YELLOW)})",
                w,
            ))
        lines.append(box_empty(w))

    comparison_row("Tokens", d_tokens, cf_tokens, format_tokens,
                   token_saved, token_pct)
    comparison_row("Estimated Cost", d_cost, cf_cost, format_usd,
                   cost_saved, cost_pct)
    comparison_row("Avg Latency", d_lat, cf_lat, format_ms,
                   latency_diff, latency_pct)

    # Savings bar chart
    lines.append(box_mid(w))
    lines.append(box_row(c("  Savings Summary", CYAN), w))
    lines.append(box_row("  " + "\u2500" * (w - 6), w))

    lines.append(box_row(
        f"  Token Savings  {savings_bar(max(token_pct, 0), bar_w)}  "
        f"{c(f'{token_pct:.1f}%', GREEN if token_pct > 0 else YELLOW)}",
        w,
    ))
    lines.append(box_row(
        f"  Cost Savings   {savings_bar(max(cost_pct, 0), bar_w)}  "
        f"{c(f'{cost_pct:.1f}%', GREEN if cost_pct > 0 else YELLOW)}",
        w,
    ))
    if latency_pct > 0:
        lines.append(box_row(
            f"  Latency Saved  {savings_bar(max(latency_pct, 0), bar_w)}  "
            f"{c(f'{latency_pct:.1f}%', GREEN)}",
            w,
        ))

    lines.append(box_empty(w))
    lines.append(box_row(
        c("  Results vary by provider, model, and workload.", DIM), w,
    ))

    lines.append(box_bot(w))
    print("\n".join(lines))


def render_per_prompt_comparison(direct: dict, cacheforge: dict) -> None:
    """Render per-prompt comparison table."""
    w = min(term_width(), 80)
    lines = []

    lines.append(box_top(w))
    lines.append(box_row(c("  Per-Prompt Comparison", CYAN, BOLD), w))
    lines.append(box_mid(w))

    d_results = direct.get("results", [])
    cf_results = cacheforge.get("results", [])

    for d_r, cf_r in zip(d_results, cf_results):
        name = d_r.get("name", "?")[:24]
        d_tok = d_r.get("total_tokens", 0)
        cf_tok = cf_r.get("total_tokens", 0)
        d_lat = d_r.get("latency_ms", 0)
        cf_lat = cf_r.get("latency_ms", 0)
        d_cost = d_r.get("estimated_cost_usd", 0)
        cf_cost = cf_r.get("estimated_cost_usd", 0)

        tok_delta = d_tok - cf_tok
        tok_pct = (tok_delta / d_tok * 100) if d_tok > 0 else 0

        lines.append(box_row(c(f"  {name}", WHITE, BOLD), w))

        if d_r.get("ok") and cf_r.get("ok"):
            lines.append(box_row(
                f"    Tokens:  {d_tok:>6d} \u2192 {c(str(cf_tok), GREEN):>6s}"
                f"  ({c(f'-{tok_pct:.0f}%', GREEN) if tok_pct > 0 else c('same', DIM)})",
                w,
            ))
            lines.append(box_row(
                f"    Latency: {format_ms(d_lat):>7s} \u2192 {c(format_ms(cf_lat), GREEN):>7s}"
                f"    Cost: {format_usd(d_cost):>8s} \u2192 {c(format_usd(cf_cost), GREEN):>8s}",
                w,
            ))
        else:
            if not d_r.get("ok"):
                lines.append(box_row(c("    Direct: FAILED", RED), w))
            if not cf_r.get("ok"):
                lines.append(box_row(c("    CacheForge: FAILED", RED), w))

    lines.append(box_bot(w))
    print("\n".join(lines))


# ---------------------------------------------------------------------------
# Subcommand: run
# ---------------------------------------------------------------------------

def cmd_run(args: argparse.Namespace) -> None:
    """Run a benchmark suite against a single endpoint."""
    provider = args.provider
    model = args.model
    base_url = args.url
    api_key = args.api_key
    max_tokens = args.max_tokens

    # Resolve URL
    if not base_url:
        if provider in PROVIDER_URLS:
            base_url = PROVIDER_URLS[provider]
        else:
            base_url = os.environ.get(
                "CACHEFORGE_BASE_URL", "https://app.anvil-ai.io"
            ).rstrip("/") + "/v1"

    # Resolve API key
    if not api_key:
        env_key = PROVIDER_KEY_ENVS.get(provider, "")
        if env_key:
            api_key = os.environ.get(env_key, "")
        if not api_key:
            api_key = os.environ.get("CACHEFORGE_API_KEY", "")
        if not api_key:
            print(c("Error: No API key provided. Use --api-key or set the "
                     "appropriate environment variable.", RED), file=sys.stderr)
            sys.exit(1)

    # Resolve prompts
    if args.prompts:
        prompts = load_custom_prompts(args.prompts)
    elif args.inline:
        prompts = make_inline_prompt(args.inline)
    else:
        prompts = BUILTIN_PROMPTS

    label = f"{provider}/{model}"
    data = run_benchmark(base_url, api_key, model, prompts, label, max_tokens)

    print()
    render_single_report(data)

    # Save results
    output = args.output or "results.json"
    with open(output, "w") as f:
        json.dump(data, f, indent=2)
    print(c(f"\n  Results saved to {output}", DIM))
    print()


# ---------------------------------------------------------------------------
# Subcommand: compare
# ---------------------------------------------------------------------------

def cmd_compare(args: argparse.Namespace) -> None:
    """Run A/B comparison: direct provider vs CacheForge."""
    model = args.model
    max_tokens = args.max_tokens

    direct_url = args.direct_url
    direct_key = args.direct_key
    cf_url = args.cacheforge_url or os.environ.get(
        "CACHEFORGE_BASE_URL", "https://app.anvil-ai.io"
    ).rstrip("/") + "/v1"
    cf_key = args.cacheforge_key or os.environ.get("CACHEFORGE_API_KEY", "")

    if not direct_url or not direct_key:
        print(c("Error: --direct-url and --direct-key are required.", RED),
              file=sys.stderr)
        sys.exit(1)
    if not cf_key:
        print(c("Error: --cacheforge-key or CACHEFORGE_API_KEY required.", RED),
              file=sys.stderr)
        sys.exit(1)

    # Resolve prompts
    if args.prompts:
        prompts = load_custom_prompts(args.prompts)
    elif args.inline:
        prompts = make_inline_prompt(args.inline)
    else:
        prompts = BUILTIN_PROMPTS

    w = min(term_width(), 80)
    print()
    print(box_top(w))
    print(box_row(c("  CacheForge A/B Benchmark", CYAN, BOLD), w))
    print(box_row(c(f"  Model: {model}  |  Prompts: {len(prompts)}", DIM), w))
    print(box_bot(w))

    # Run direct
    direct_data = run_benchmark(direct_url, direct_key, model, prompts,
                                "Direct Provider", max_tokens)

    # Run through CacheForge
    cf_data = run_benchmark(cf_url, cf_key, model, prompts,
                            "CacheForge", max_tokens)

    print()
    render_comparison_report(direct_data, cf_data)
    print()
    render_per_prompt_comparison(direct_data, cf_data)

    # Save combined results
    output = args.output or "comparison.json"
    combined = {
        "type": "comparison",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "model": model,
        "direct": direct_data,
        "cacheforge": cf_data,
    }
    with open(output, "w") as f:
        json.dump(combined, f, indent=2)
    print(c(f"\n  Results saved to {output}", DIM))
    print()


# ---------------------------------------------------------------------------
# Subcommand: report
# ---------------------------------------------------------------------------

def cmd_report(args: argparse.Namespace) -> None:
    """Re-render a report from saved JSON results."""
    input_file = args.input
    if not os.path.exists(input_file):
        print(c(f"Error: file not found: {input_file}", RED), file=sys.stderr)
        sys.exit(1)

    with open(input_file, "r") as f:
        data = json.load(f)

    if data.get("type") == "comparison":
        render_comparison_report(data["direct"], data["cacheforge"])
        print()
        render_per_prompt_comparison(data["direct"], data["cacheforge"])
    else:
        render_single_report(data)

    print()


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        prog="cacheforge-bench",
        description="CacheForge Benchmark Runner — LLM cost benchmarks with and without CacheForge.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Environment variables:\n"
            "  CACHEFORGE_BASE_URL    CacheForge endpoint (default: https://app.anvil-ai.io)\n"
            "  CACHEFORGE_API_KEY     CacheForge API key\n"
            "  OPENAI_API_KEY         OpenAI API key\n"
            "  ANTHROPIC_API_KEY      Anthropic API key\n"
            "  OPENROUTER_API_KEY     OpenRouter API key\n"
            "\n"
            "Examples:\n"
            "  python3 bench.py run --provider openai --model gpt-4o-mini\n"
            "  python3 bench.py compare --direct-url https://api.openai.com/v1 \\\n"
            "      --direct-key $KEY --cacheforge-key $CF_KEY\n"
            "  python3 bench.py report --input results.json\n"
        ),
    )
    sub = parser.add_subparsers(dest="command")

    # run
    p_run = sub.add_parser("run", help="Run benchmark suite against a provider")
    p_run.add_argument("--provider", default="openai",
                       choices=["openai", "openrouter", "cacheforge", "custom"],
                       help="Provider name (default: openai)")
    p_run.add_argument("--model", default="gpt-4o-mini",
                       help="Model name (default: gpt-4o-mini)")
    p_run.add_argument("--url", default=None,
                       help="Custom base URL (overrides provider default)")
    p_run.add_argument("--api-key", default=None,
                       help="API key (or use env var)")
    p_run.add_argument("--prompts", default=None,
                       help="Path to custom prompts JSON file")
    p_run.add_argument("--inline", default=None,
                       help="Inline prompt text for single-prompt benchmark")
    p_run.add_argument("--max-tokens", type=int, default=256,
                       help="Max tokens per completion (default: 256)")
    p_run.add_argument("--output", default=None,
                       help="Output JSON file (default: results.json)")

    # compare
    p_cmp = sub.add_parser("compare", help="A/B comparison: direct vs CacheForge")
    p_cmp.add_argument("--direct-url", required=True,
                       help="Direct provider base URL")
    p_cmp.add_argument("--direct-key", required=True,
                       help="Direct provider API key")
    p_cmp.add_argument("--cacheforge-url", default=None,
                       help="CacheForge endpoint URL (or use CACHEFORGE_BASE_URL)")
    p_cmp.add_argument("--cacheforge-key", default=None,
                       help="CacheForge API key (or use CACHEFORGE_API_KEY)")
    p_cmp.add_argument("--model", default="gpt-4o-mini",
                       help="Model name (default: gpt-4o-mini)")
    p_cmp.add_argument("--prompts", default=None,
                       help="Path to custom prompts JSON file")
    p_cmp.add_argument("--inline", default=None,
                       help="Inline prompt text for single-prompt benchmark")
    p_cmp.add_argument("--max-tokens", type=int, default=256,
                       help="Max tokens per completion (default: 256)")
    p_cmp.add_argument("--output", default=None,
                       help="Output JSON file (default: comparison.json)")

    # report
    p_rpt = sub.add_parser("report", help="Re-render report from saved JSON")
    p_rpt.add_argument("--input", required=True,
                       help="Path to results JSON file")

    args = parser.parse_args()

    if args.command is None:
        parser.print_help()
        sys.exit(0)

    dispatch = {
        "run": cmd_run,
        "compare": cmd_compare,
        "report": cmd_report,
    }

    handler = dispatch.get(args.command)
    if handler:
        handler(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
