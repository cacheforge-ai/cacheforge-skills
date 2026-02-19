# cacheforge-bench

LLM cost benchmark runner — compare providers with and without CacheForge. See exactly what you save on your own workloads.

## Quick Start

```bash
# Run the built-in benchmark suite against OpenAI
python3 bench.py run --provider openai --model gpt-4o-mini --api-key $OPENAI_API_KEY

# Compare direct provider costs vs CacheForge
python3 bench.py compare \
    --direct-url https://api.openai.com/v1 --direct-key $OPENAI_API_KEY \
    --cacheforge-url https://app.anvil-ai.io/v1 --cacheforge-key $CACHEFORGE_API_KEY

# Re-render a saved report
python3 bench.py report --input results.json
```

## Features

- **Quick benchmark** — Run a standard prompt suite against any OpenAI-compatible endpoint. Measures tokens, latency, and estimated cost.
- **A/B comparison** — Run the same suite through a direct provider and through CacheForge side-by-side. See the exact delta in tokens, cost, and latency.
- **Custom prompts** — Bring your own prompt files or inline prompts to benchmark your real workloads.
- **Terminal reports** — Rich terminal output with Unicode box drawing, ANSI colours, and bar charts.
- **JSON export** — All results saved as JSON for programmatic consumption.

## Environment Variables

| Variable | Description |
|---|---|
| `CACHEFORGE_BASE_URL` | CacheForge endpoint (default: `https://app.anvil-ai.io`) |
| `CACHEFORGE_API_KEY` | CacheForge API key |
| `OPENAI_API_KEY` | OpenAI API key |
| `ANTHROPIC_API_KEY` | Anthropic API key |
| `OPENROUTER_API_KEY` | OpenRouter API key |

## Built-in Prompt Suite

The benchmark includes 6 heavy prompts representing real agent workloads:

- Browser snapshot analysis (full accessibility tree payload)
- HTML page processing (large dashboard page extraction)
- JSON API response analysis (structured data with nested objects)
- Heavy tool schema (10 tool definitions — typical agent framework overhead)
- Multi-turn with tool results (accumulated context with prior web fetch outputs)
- Repeated heavy context (same browser snapshot, different question — cache-hit potential)

## Custom Prompts

Create a JSON file with an array of prompt objects:

```json
[
  {
    "name": "My Prompt",
    "description": "What this tests",
    "messages": [
      {"role": "user", "content": "Your prompt here"}
    ]
  }
]
```

Then run:

```bash
python3 bench.py run --provider openai --model gpt-4o-mini --prompts my-prompts.json
```

## Requirements

- Python 3.8+ (stdlib only — no pip install needed)

## Notes

- Savings of up to 30% or more are typical, but results vary by provider, model, and workload.
- Cost estimates use approximate public pricing.
- All API calls use the OpenAI-compatible chat completions format.

## Install

```bash
clawhub install cacheforge-bench
```

Or clone from [GitHub](https://github.com/cacheforge-ai/cacheforge-skills).

## License

MIT — see [LICENSE](LICENSE).

---

Part of the [CacheForge](https://app.anvil-ai.io) toolkit — enterprise-grade LLM optimization for agent workflows.
