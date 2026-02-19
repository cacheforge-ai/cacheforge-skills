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

The benchmark includes 6 diverse prompts covering:

- Short chat (baseline latency)
- Long system prompt + short query (cache-hit potential)
- Tool-heavy request with JSON (Vault Mode potential)
- Multi-turn conversation (context accumulation)
- Code generation (medium complexity)
- Repeated system prompt with different query (cache-hit potential)

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

## License

MIT — see [LICENSE](LICENSE).

## Links

- [CacheForge](https://app.anvil-ai.io)
