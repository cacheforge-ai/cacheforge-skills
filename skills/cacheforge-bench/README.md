# CacheForge Bench

Benchmark runner for comparing LLM request behavior across endpoints.

## Quick Start

```bash
# Run built-in suite against an OpenAI-compatible endpoint
python3 bench.py run --provider openai --model gpt-4o-mini --api-key $OPENAI_API_KEY

# Compare direct provider vs gateway endpoint
python3 bench.py compare \
    --direct-url https://api.openai.com/v1 --direct-key $OPENAI_API_KEY \
    --cacheforge-url https://<cacheforge-endpoint>/v1 --cacheforge-key $CACHEFORGE_API_KEY

# Re-render a saved report
python3 bench.py report --input results.json
```

## License

MIT
