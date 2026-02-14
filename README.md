# CacheForge — Agent Skills

Cut your agent's token bill by up to 93%. CacheForge is a drop-in optimization layer that sits between your agent and your LLM provider. Proprietary multi-layer optimization that goes far beyond caching. One line of config. Zero code changes.

## Install

```bash
# Install the full CacheForge skill pack (recommended)
for s in cacheforge cacheforge-setup cacheforge-ops cacheforge-stats; do
  clawhub install "$s"
done
```

## Skills

| Skill | What it does |
|-------|--------------|
| `cacheforge` | Connect any OpenAI-compatible agent to CacheForge. Configure providers, verify telemetry. |
| `cacheforge-setup` | Guided onboarding — register, configure upstream, get your API key in 30 seconds. |
| `cacheforge-ops` | Account operations — check balance, top up (crypto or card), manage API keys, configure upstream. |
| `cacheforge-stats` | Terminal dashboard — usage, savings, token reduction, cost breakdown with sparklines and bar charts. |

## Quick Start

```bash
# Install the full skill pack
for s in cacheforge cacheforge-setup cacheforge-ops cacheforge-stats; do clawhub install "$s"; done

# Guided setup (auto-detects your existing API keys)
/cacheforge-setup

# Check your savings
/cacheforge-stats

# Check balance or top up
/cacheforge-ops balance
/cacheforge-ops topup --amount 10
```

Or skip the wizard — one env var is all you need:

```bash
export OPENAI_BASE_URL=https://app.anvil-ai.io/v1
export OPENAI_API_KEY=cfk_...  # your CacheForge key
```

If this deployment is invite-only, also set:

```bash
export CACHEFORGE_INVITE_CODE=...
```

Every OpenAI-compatible tool (OpenClaw, Claude Code, Cursor, Codex CLI, any agent framework) routes through CacheForge automatically.

## What CacheForge Does

CacheForge sits between your agent and your LLM provider (OpenAI, Anthropic, OpenRouter). It applies proprietary multi-layer optimization to fundamentally reduce what gets sent to your provider. Up to 93% token reduction on heavy workloads. Provider-reported usage plus transparent savings telemetry.

Not a cache. Not a proxy trick. The how is our secret.

## Agent-Native by Design

- **Your agent is its own bank** — Top up with USDC, SOL, or credit card. Your agent can check its balance and fund itself autonomously via API.
- **Full management API** — Billing, account, and key management. Built for agents that manage themselves.
- **Telegram alerts** — Link your Telegram for low-balance warnings, top-up confirmations, and status checks.
- **No subscription required** — Prepaid credits. Pay-as-you-go.

## Built on Open Standards

CacheForge ships as an Agent Skill — the open standard by Anthropic, adopted by Claude Code, OpenAI Codex, Cursor, Gemini CLI, OpenClaw, and dozens more. Install once, optimize everywhere.

## Links

- **Console**: [app.anvil-ai.io](https://app.anvil-ai.io)
- **Privacy**: [app.anvil-ai.io/privacy](https://app.anvil-ai.io/privacy)
- **Terms**: [app.anvil-ai.io/terms](https://app.anvil-ai.io/terms)

## License

MIT
