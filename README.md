# CacheForge — Agent Skills

Cut your agent's token bill by up to 30% or more. CacheForge is a drop-in proxy that sits between your agent and your LLM provider. One line of config. Zero code changes. The Pied Piper of token compression.

Heavy tool, browser, and JSON workloads with Vault Mode can see dramatically higher savings. Results vary by provider, model, and workload.

## Install

```bash
# Install the full CacheForge skill pack
for s in cacheforge cacheforge-setup cacheforge-ops cacheforge-stats cacheforge-bench context-engineer agentic-devops; do
  clawhub install "$s"
done
```

## Skills

### 💰 CacheForge SaaS — Onboard, Manage, Optimize

| Skill | What it does |
|-------|--------------|
| [`cacheforge`](skills/cacheforge/) | Connect any OpenAI-compatible agent to CacheForge. Configure providers, verify telemetry. |
| [`cacheforge-setup`](skills/cacheforge-setup/) | Guided onboarding — register, configure upstream, get your API key in 30 seconds. |
| [`cacheforge-ops`](skills/cacheforge-ops/) | Account operations — check balance, top up (crypto or card), manage API keys, configure upstream. |
| [`cacheforge-stats`](skills/cacheforge-stats/) | Terminal dashboard — usage, savings, token reduction, cost breakdown with sparklines and bar charts. |

### 🔧 CacheForge Engineering — Tools Built by Production Engineers

| Skill | What it does |
|-------|--------------|
| [`cacheforge-bench`](skills/cacheforge-bench/) | LLM cost benchmark runner — compare providers with and without CacheForge on your own workloads. |
| [`context-engineer`](skills/context-engineer/) | Context window optimizer — analyze, audit, and optimize your agent's context utilization. |
| [`agentic-devops`](skills/agentic-devops/) | Production-grade DevOps toolkit — Docker, process management, log analysis, health monitoring. |

## Quick Start

```bash
# Install core CacheForge skills
for s in cacheforge cacheforge-setup cacheforge-ops cacheforge-stats; do clawhub install "$s"; done

# Guided setup (auto-detects your existing API keys)
/cacheforge-setup

# Check your savings
/cacheforge-stats

# Check balance or top up
/cacheforge-ops balance
/cacheforge-ops topup --amount 10

# Benchmark your savings
/cacheforge-bench compare --direct-url https://api.openai.com/v1 --direct-key $KEY --cacheforge-key $CF_KEY

# Analyze your context utilization
/context-engineer report --workspace ~/.openclaw/workspace

# Full system diagnostics
/agentic-devops diag
```

Or skip the wizard — one env var is all you need:

```bash
export OPENAI_BASE_URL=https://app.anvil-ai.io/v1
export OPENAI_API_KEY=cf_...  # your CacheForge key
```

Every OpenAI-compatible tool (OpenClaw, Claude Code, Cursor, Codex CLI, any agent framework) routes through CacheForge automatically.

## What CacheForge Does

CacheForge sits between your agent and your LLM provider (OpenAI, Anthropic, OpenRouter). It fundamentally reduces what gets sent to your provider — up to 30% or more on typical workloads, dramatically higher on heavy tool/browser/JSON payloads with Vault Mode.

The heavier your agent traffic, the more you save. Browser automation, structured data, tool-heavy workflows — that's where CacheForge shines brightest.

Provider-reported usage. Transparent savings telemetry. Lossless.

## Agent-Native by Design

- **Your agent is its own bank** — Top up with USDC, SOL, or credit card. Your agent can check its balance and fund itself autonomously via API.
- **Full management API** — Billing, account, and key management. Built for agents that manage themselves.
- **No subscription required** — Prepaid credits. Pay-as-you-go.

## Built on Open Standards

CacheForge ships as Agent Skills — the open standard by Anthropic, adopted by Claude Code, OpenAI Codex, Cursor, Gemini CLI, OpenClaw, and dozens more. Install once, optimize everywhere.

## Links

- **Console**: [app.anvil-ai.io](https://app.anvil-ai.io)
- **GitHub**: [github.com/cacheforge-ai/cacheforge-skills](https://github.com/cacheforge-ai/cacheforge-skills)
- **ClawHub**: [clawhub.ai/skills/cacheforge](https://clawhub.ai/skills/cacheforge)

## License

MIT — [CacheForge](https://app.anvil-ai.io)
