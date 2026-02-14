---
name: cacheforge-setup
description: Set up CacheForge — register, configure upstream, get your API key in 30 seconds.
license: MIT
homepage: https://app.anvil-ai.io
user-invocable: true
metadata: {"openclaw":{"emoji":"⚒️","homepage":"https://app.anvil-ai.io","requires":{"bins":["python3"]}}}
---

## When to use this skill

Use this skill when the user wants to:
- Set up CacheForge for the first time
- Register a new CacheForge account
- Connect their LLM API provider to CacheForge
- Get a CacheForge API key

## Setup Flow

1. **Detect existing API keys** — Check for `OPENAI_API_KEY`, `OPENROUTER_API_KEY`, `ANTHROPIC_API_KEY` in the environment
2. **Collect credentials** — Ask user for email and password if not provided
3. **Auto-detect provider** — Infer upstream kind from key prefix:
   - `sk-or-` → openrouter
   - `sk-ant-` → anthropic
   - `sk-` → openai
4. **Provision** — Run `python setup.py provision` to register/authenticate and get a CacheForge API key
5. **Validate** — Run `python setup.py validate` to make a test request through the proxy
6. **Configure OpenClaw** — Show the user how to add CacheForge as a provider

## Commands

```bash
# Full setup (interactive)
python skills/cacheforge-setup/setup.py provision \
  --email user@example.com \
  --password "..." \
  --invite-code "..." \
  --upstream-kind openrouter \
  --upstream-key sk-or-...

# Just validate an existing setup
python skills/cacheforge-setup/setup.py validate \
  --base-url https://app.anvil-ai.io \
  --api-key cfk_...
```

## Environment Variables

- `CACHEFORGE_BASE_URL` — CacheForge API base (default: https://app.anvil-ai.io)
- `CACHEFORGE_API_KEY` — Existing API key (skip provisioning if set)
- `CACHEFORGE_INVITE_CODE` — Invite code (required on invite-only deployments)
- `OPENAI_API_KEY`, `OPENROUTER_API_KEY`, `ANTHROPIC_API_KEY` — Auto-detected for upstream

## After Setup

Once provisioned, set:
```bash
export OPENAI_BASE_URL=https://app.anvil-ai.io/v1
export OPENAI_API_KEY=cfk_...  # your CacheForge key
```

All OpenAI-compatible tools (OpenClaw, Claude Code, Cursor, any agent framework) will route through CacheForge automatically.

## API Contract (current)

This skill uses:
- `POST /api/provision`
- `GET /v1/account/info`
