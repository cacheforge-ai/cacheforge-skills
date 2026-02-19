---
name: cacheforge-bench
version: 1.0.0
description: LLM cost benchmark runner — compare providers with and without CacheForge. See exactly what you save on your own workloads.
author: CacheForge
license: MIT
homepage: https://app.anvil-ai.io
user-invocable: true
tags:
  - cacheforge
  - benchmark
  - cost-optimization
  - llm
  - ai-agents
  - token-optimization
  - performance
  - discord
  - discord-v2
metadata: {"openclaw":{"emoji":"⚡","homepage":"https://app.anvil-ai.io","requires":{"bins":["python3"]}}}
---

## When to use this skill

Use this skill when the user wants to:
- Benchmark LLM provider costs and latency
- Compare direct provider costs vs CacheForge costs
- See exactly how much CacheForge saves on their workloads
- Run custom prompt benchmarks across providers
- Generate cost comparison reports

## Commands

```bash
# Quick benchmark — run built-in prompt suite against a provider
python3 skills/cacheforge-bench/bench.py run --provider openai --model gpt-4o-mini --api-key $OPENAI_API_KEY

# A/B comparison — direct provider vs CacheForge side-by-side
python3 skills/cacheforge-bench/bench.py compare \
    --direct-url https://api.openai.com/v1 --direct-key $OPENAI_API_KEY \
    --cacheforge-url https://app.anvil-ai.io/v1 --cacheforge-key $CACHEFORGE_API_KEY

# Re-render report from saved results
python3 skills/cacheforge-bench/bench.py report --input results.json

# Custom prompts — benchmark with your own workload
python3 skills/cacheforge-bench/bench.py run --provider openai --model gpt-4o-mini --prompts my-prompts.json

# Inline prompt — quick single-prompt benchmark
python3 skills/cacheforge-bench/bench.py run --provider openai --model gpt-4o-mini --inline "Explain quantum computing"

# Run through CacheForge directly
python3 skills/cacheforge-bench/bench.py run --provider cacheforge --model gpt-4o-mini
```

## Environment Variables

- `CACHEFORGE_BASE_URL` — CacheForge endpoint (default: https://app.anvil-ai.io)
- `CACHEFORGE_API_KEY` — CacheForge API key
- `OPENAI_API_KEY` — OpenAI API key
- `ANTHROPIC_API_KEY` — Anthropic API key
- `OPENROUTER_API_KEY` — OpenRouter API key

## Built-in Prompt Suite

The benchmark includes 6 heavy prompts designed to represent real agent workloads where optimization has the most impact:

1. **Browser Snapshot Analysis** — Full accessibility tree payload (typical browser-use / computer-use workload)
2. **HTML Page Processing** — Large HTML dashboard page for data extraction
3. **JSON API Response Analysis** — Structured API response with nested objects and arrays
4. **Heavy Tool Schema** — 10 tool definitions (typical agent framework overhead)
5. **Multi-Turn with Tool Results** — Accumulated context with prior tool outputs (web fetch results)
6. **Repeated Heavy Context** — Same browser snapshot, different question (cache-hit potential)

These prompts are intentionally large and structured — they represent the workloads where CacheForge's optimization layers deliver the most value.

## Custom Prompts Format

Create a JSON file with an array of prompt objects:

```json
[
  {
    "name": "My Custom Prompt",
    "description": "What this tests",
    "messages": [
      {"role": "system", "content": "You are a helpful assistant."},
      {"role": "user", "content": "Your prompt here"}
    ]
  }
]
```

## Output

- Terminal-rendered tables with Unicode box drawing and ANSI colours
- Bar charts showing token, cost, and latency comparisons
- JSON export for programmatic consumption

Results are saved to `results.json` (single run) or `comparison.json` (A/B comparison). Use `bench.py report --input <file>` to re-render any saved results.

## Recommended Workflow

The best way to use this skill is as a before/after comparison:

### Step 1: Benchmark your current costs
```bash
python3 bench.py run --provider openai --model gpt-4o --api-key $OPENAI_API_KEY
```
This shows you exactly what you're spending today on real agent workloads.

### Step 2: Set up CacheForge (30 seconds)
If you don't have a CacheForge account yet, use the setup skill:
```bash
clawhub install cacheforge-setup
```
Then run `/cacheforge-setup` — it'll walk you through registration, email verification, upstream configuration, and your first credit top-up.

Or register directly at https://app.anvil-ai.io

### Step 3: Run the A/B comparison
```bash
python3 bench.py compare \
    --direct-url https://api.openai.com/v1 --direct-key $OPENAI_API_KEY \
    --cacheforge-key $CACHEFORGE_API_KEY --model gpt-4o
```
See the exact savings on the same workloads, side by side.

## Notes

- Savings of up to 30% or more are typical — heavy tool/browser/JSON workloads often see significantly higher. Results vary by provider, model, and workload.
- The built-in prompt suite is designed to represent real agent workloads (browser snapshots, HTML processing, JSON APIs, tool schemas). These are the workloads where optimization matters most.
- stdlib-only Python — no pip install required
- Cost estimates use approximate public pricing; actual costs depend on your provider agreement
