---
name: cacheforge
description: Connect OpenClaw to CacheForge — proprietary optimization that cuts your agent's token bill by up to 93%.
license: MIT
homepage: https://app.anvil-ai.io
user-invocable: true
metadata: {"openclaw":{"emoji":"🧠","homepage":"https://app.anvil-ai.io"}}
---

## When to use this skill

Use this skill when the user asks to:
- connect OpenClaw to a **proxy / gateway** to reduce token spend
- configure **models.providers** (OpenAI-compatible, Anthropic Messages)
- validate that **prompt caching** is working and measure cached tokens

## What CacheForge is

CacheForge is a drop-in optimization layer in front of OpenAI / OpenRouter / Anthropic that:
- applies proprietary multi-layer optimization to reduce token usage by up to 93%
- injects `stream_options.include_usage=true` for OpenAI-compatible streaming, so cached tokens are visible
- logs usage and latency per request
- exposes a real-time savings dashboard

## Setup (OpenAI-compatible)

1) In CacheForge Console → Settings:
- Create a tenant API key (`cfk_...`)
- Configure your upstream provider and upstream API key

2) In your OpenClaw config (`~/.openclaw/openclaw.json`), add a provider:

```jsonc
{
  "models": {
    "mode": "merge",
    "providers": {
      "cacheforge": {
        "baseUrl": "https://app.anvil-ai.io/v1",
        "apiKey": "${CACHEFORGE_API_KEY}",
        "api": "openai-completions",
        "models": [
          { "id": "gpt-4o-mini", "name": "GPT-4o mini" }
        ]
      }
    }
  },
  "agents": {
    "defaults": { "model": { "primary": "cacheforge/gpt-4o-mini" } }
  }
}
```

3) Provide the key to OpenClaw safely (choose one):

### Option A: Environment variable
Set `CACHEFORGE_API_KEY` in your shell / service env, then launch OpenClaw.

### Option B: OpenClaw skills entries (per-run injection)
Add:

```jsonc
{
  "skills": {
    "entries": {
      "cacheforge": {
        "enabled": true,
        "env": { "CACHEFORGE_API_KEY": "cf_live_...YOUR_KEY..." }
      }
    }
  }
}
```

## Setup (Anthropic Messages)

Use `api: "anthropic-messages"` and point at the same baseUrl:

```jsonc
{
  "models": {
    "providers": {
      "cacheforge_anthropic": {
        "baseUrl": "https://app.anvil-ai.io",
        "apiKey": "${CACHEFORGE_API_KEY}",
        "api": "anthropic-messages",
        "models": [{ "id": "claude-3-7-sonnet-latest", "name": "Claude Sonnet" }]
      }
    }
  }
}
```

CacheForge routes `/v1/messages` to the configured upstream.

## Validate caching + telemetry

- Open CacheForge dashboard → Requests (7d) should increase.
- Cached tokens will show up when the provider supports caching and your prompts are long/repetitive enough.

Tip: If you stream OpenAI-compatible responses, CacheForge will request usage in-stream automatically.
