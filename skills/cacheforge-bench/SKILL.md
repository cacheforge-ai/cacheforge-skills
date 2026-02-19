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

The benchmark includes 6 diverse prompts designed to exercise different optimization scenarios:

1. **Short Chat** — Baseline latency with a minimal prompt
2. **Long System Prompt** — Large system prompt with short query (cache-hit potential)
3. **Tool-Heavy Request** — JSON tool definitions (Vault Mode potential)
4. **Multi-Turn Conversation** — 4-turn dialogue with context accumulation
5. **Code Generation** — Medium complexity Python class generation
6. **Repeated System Prompt** — Same system prompt, different query (cache-hit potential)

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

## Notes

- Savings of up to 30% or more are typical, but results vary by provider, model, and workload
- stdlib-only Python — no pip install required
- Cost estimates use approximate public pricing; actual costs depend on your provider agreement
