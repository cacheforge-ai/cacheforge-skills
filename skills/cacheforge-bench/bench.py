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
RED = "\033[31m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
CYAN = "\033[36m"
WHITE = "\033[37m"
MAGENTA = "\033[35m"


def c(text: str, *codes: str) -> str:
    """Wrap *text* in ANSI colour escape sequences."""
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
    pad = max(w - 2 - visible_len, 0)
    if visible_len + 2 < w:
        return "\u2502 " + text + " " * pad + " \u2502"
    return "\u2502" + strip_ansi(text)[: w - 2] + "\u2502"


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
    "anthropic": "https://api.anthropic.com/v1",
    "openrouter": "https://openrouter.ai/api/v1",
}

PROVIDER_KEY_ENVS = {
    "openai": "OPENAI_API_KEY",
    "anthropic": "ANTHROPIC_API_KEY",
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

BUILTIN_PROMPTS = [
    {
        "name": "Short Chat",
        "description": "Baseline latency — minimal prompt",
        "messages": [
            {"role": "user", "content": "What is 2 + 2?"},
        ],
    },
    {
        "name": "Long System Prompt",
        "description": "Cache-hit potential — large system prompt, short query",
        "messages": [
            {
                "role": "system",
                "content": (
                    "You are an expert financial analyst with deep knowledge of "
                    "global markets, derivatives, risk management, portfolio theory, "
                    "macroeconomic indicators, central bank policies, and quantitative "
                    "finance. You specialize in analyzing market trends, evaluating "
                    "investment strategies, and providing detailed risk assessments. "
                    "Your analysis should be thorough, data-driven, and consider "
                    "multiple perspectives including bull and bear cases. Always "
                    "provide specific metrics, ratios, and benchmarks when relevant. "
                    "Consider regulatory implications, geopolitical risks, and "
                    "cross-asset correlations in your analysis. When discussing "
                    "strategies, include risk-adjusted return metrics such as Sharpe "
                    "ratio, Sortino ratio, and maximum drawdown. Provide your "
                    "analysis in a structured format with clear sections for "
                    "executive summary, detailed analysis, risk factors, and "
                    "actionable recommendations. Always caveat your analysis with "
                    "appropriate disclaimers about market uncertainty and the "
                    "limitations of any predictive model."
                ),
            },
            {"role": "user", "content": "What's the outlook for US treasuries this quarter?"},
        ],
    },
    {
        "name": "Tool-Heavy Request",
        "description": "Vault Mode potential — JSON tool definitions",
        "messages": [
            {
                "role": "system",
                "content": "You are a helpful assistant with access to tools.",
            },
            {
                "role": "user",
                "content": json.dumps({
                    "query": "Look up the weather in San Francisco and book a restaurant",
                    "tools": [
                        {
                            "type": "function",
                            "function": {
                                "name": "get_weather",
                                "description": "Get current weather for a location",
                                "parameters": {
                                    "type": "object",
                                    "properties": {
                                        "location": {"type": "string", "description": "City name"},
                                        "units": {"type": "string", "enum": ["celsius", "fahrenheit"]},
                                    },
                                    "required": ["location"],
                                },
                            },
                        },
                        {
                            "type": "function",
                            "function": {
                                "name": "search_restaurants",
                                "description": "Search for restaurants by cuisine and location",
                                "parameters": {
                                    "type": "object",
                                    "properties": {
                                        "location": {"type": "string"},
                                        "cuisine": {"type": "string"},
                                        "price_range": {"type": "string", "enum": ["$", "$$", "$$$", "$$$$"]},
                                        "party_size": {"type": "integer"},
                                    },
                                    "required": ["location"],
                                },
                            },
                        },
                        {
                            "type": "function",
                            "function": {
                                "name": "make_reservation",
                                "description": "Make a restaurant reservation",
                                "parameters": {
                                    "type": "object",
                                    "properties": {
                                        "restaurant_id": {"type": "string"},
                                        "date": {"type": "string", "format": "date"},
                                        "time": {"type": "string"},
                                        "party_size": {"type": "integer"},
                                    },
                                    "required": ["restaurant_id", "date", "time", "party_size"],
                                },
                            },
                        },
                    ],
                }),
            },
        ],
    },
    {
        "name": "Multi-Turn Conversation",
        "description": "Context accumulation — 4-turn dialogue",
        "messages": [
            {"role": "system", "content": "You are a helpful coding assistant."},
            {"role": "user", "content": "I need to build a REST API in Python. What framework should I use?"},
            {"role": "assistant", "content": "For a REST API in Python, I'd recommend FastAPI. It's modern, fast, has automatic OpenAPI docs, and great type hints support. Flask is also a solid choice if you prefer simplicity."},
            {"role": "user", "content": "Let's go with FastAPI. How do I set up the project structure?"},
            {"role": "assistant", "content": "Here's a recommended structure:\n\n```\nmy-api/\n  app/\n    __init__.py\n    main.py\n    routers/\n    models/\n    schemas/\n  tests/\n  requirements.txt\n```\n\nStart with `main.py` as the entry point with your FastAPI app instance."},
            {"role": "user", "content": "Now add a users endpoint with CRUD operations and Pydantic models."},
        ],
    },
    {
        "name": "Code Generation",
        "description": "Medium complexity — generate a Python class",
        "messages": [
            {
                "role": "user",
                "content": (
                    "Write a Python class called `LRUCache` that implements a "
                    "least-recently-used cache with the following features:\n"
                    "- Constructor takes `capacity: int`\n"
                    "- `get(key)` returns the value or -1 if not found\n"
                    "- `put(key, value)` inserts or updates the value\n"
                    "- Both operations should be O(1) time complexity\n"
                    "- Use a doubly linked list and a hash map\n"
                    "- Include type hints and a docstring"
                ),
            },
        ],
    },
    {
        "name": "Repeated System Prompt",
        "description": "Cache-hit potential — identical system prompt, different query",
        "messages": [
            {
                "role": "system",
                "content": (
                    "You are an expert financial analyst with deep knowledge of "
                    "global markets, derivatives, risk management, portfolio theory, "
                    "macroeconomic indicators, central bank policies, and quantitative "
                    "finance. You specialize in analyzing market trends, evaluating "
                    "investment strategies, and providing detailed risk assessments. "
                    "Your analysis should be thorough, data-driven, and consider "
                    "multiple perspectives including bull and bear cases. Always "
                    "provide specific metrics, ratios, and benchmarks when relevant. "
                    "Consider regulatory implications, geopolitical risks, and "
                    "cross-asset correlations in your analysis. When discussing "
                    "strategies, include risk-adjusted return metrics such as Sharpe "
                    "ratio, Sortino ratio, and maximum drawdown. Provide your "
                    "analysis in a structured format with clear sections for "
                    "executive summary, detailed analysis, risk factors, and "
                    "actionable recommendations. Always caveat your analysis with "
                    "appropriate disclaimers about market uncertainty and the "
                    "limitations of any predictive model."
                ),
            },
            {"role": "user", "content": "Summarize the key risks of investing in emerging market bonds."},
        ],
    },
]


# ---------------------------------------------------------------------------
# HTTP helpers
# ---------------------------------------------------------------------------

def _openai_chat(base_url: str, api_key: str, model: str,
                 messages: list, max_tokens: int = 256) -> dict:
    """Send a chat completion request (OpenAI-compatible API)."""
    url = f"{base_url.rstrip('/')}/chat/completions"
    payload = json.dumps({
        "model": model,
        "messages": messages,
        "max_tokens": max_tokens,
    }).encode()

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
                            prompt["messages"], max_tokens)

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
                       choices=["openai", "anthropic", "openrouter", "cacheforge", "custom"],
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
