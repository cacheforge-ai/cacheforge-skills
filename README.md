# CacheForge — Agent Skills

CacheForge is a drop-in, OpenAI-compatible gateway for agent workflows. It can reduce wasted LLM spend by up to 30% or more and improve repeat-turn performance (results vary by provider/workload).

## Install

```bash
# Install the primary CacheForge skill (recommended)
clawhub install cacheforge
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
# Install the primary skill
clawhub install cacheforge

# Primary entrypoint (bootstraps companion skills if missing)
/cacheforge

# If invite-only + email verification are enabled, verify your email,
# then run /cacheforge again to continue setup and mint your tenant API key (cf_...).

# Setup can print and (with approval) apply OpenClaw config with backup:
# ~/.openclaw/openclaw.json + .cacheforge.bak

# Check your savings
/cacheforge-stats

# Check balance or top up (minimum top-up is typically $10)
/cacheforge-ops balance
/cacheforge-ops topup --amount 10 --method stripe
/cacheforge-ops topup --amount 10 --method crypto
```

Or skip the wizard — one env var is all you need:

```bash
export OPENAI_BASE_URL=https://app.anvil-ai.io/v1
export OPENAI_API_KEY=cf_...  # your CacheForge tenant API key
```

If this deployment is invite-only, also set:

```bash
export CACHEFORGE_INVITE_CODE=...
```

Every OpenAI-compatible tool (OpenClaw, Claude Code, Cursor, Codex CLI, any agent framework) routes through CacheForge automatically.

Note: `cacheforge` is the primary entrypoint. It can bootstrap companion skills (`cacheforge-setup`, `cacheforge-ops`, `cacheforge-stats`) when needed.

## What CacheForge Does

CacheForge sits between your agent and your LLM provider (OpenAI, Anthropic, OpenRouter). It applies proprietary multi-layer optimization for agent workloads and surfaces transparent telemetry so teams can verify impact in the dashboard.

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
