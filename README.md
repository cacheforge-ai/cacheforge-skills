<div align="center">

# 🔥 CacheForge Agent Skills

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Skills](https://img.shields.io/badge/skills-10-blue.svg)](#skills)
[![ClawHub](https://img.shields.io/badge/ClawHub-published-green.svg)](https://clawhub.com)
[![OpenClaw](https://img.shields.io/badge/OpenClaw-v2026.2.14+-purple.svg)](https://github.com/moltbot/moltbot)
[![Discord v2](https://img.shields.io/badge/Discord-v2%20ready-5865F2.svg)](#discord-v2-ready)
[![Powered by CacheForge](https://img.shields.io/badge/Powered%20by-CacheForge-ff6b35.svg)](https://app.anvil-ai.io)

**Production-grade Agent Skills for [OpenClaw](https://github.com/moltbot/moltbot) and the [ClawHub](https://clawhub.com) marketplace.**

Built by [CacheForge](https://app.anvil-ai.io) — making AI agents affordable, powerful, and production-ready.

---

*Real CLI integrations. Safe by default. Discord v2 ready. 30M+ tokens battle-tested.*

</div>

## Skills

### 🔍 Code Quality & Security

| Skill | Description | Version | Install |
|-------|-------------|---------|---------|
| [vibe-check](skills/vibe-check/) | Code quality auditor — catches "vibe coding" sins | 0.1.1 | `clawhub install vibe-check` |
| [dep-audit](skills/dep-audit/) | Dependency vulnerability scanner (npm, pip, Cargo, Go, Ruby) | 0.1.3 | `clawhub install dep-audit` |
| [rug-checker](skills/rug-checker/) | Solana token rug-pull risk analysis (10-point scoring) | 0.1.3 | `clawhub install rug-checker` |

### 📡 Observability & Infrastructure

| Skill | Description | Version | Install |
|-------|-------------|---------|---------|
| [prom-query](skills/prom-query/) | Prometheus metrics query & alert interpreter | 1.0.1 | `clawhub install prom-query` |
| [kube-medic](skills/kube-medic/) | Kubernetes cluster triage & pod autopsy | 1.0.1 | `clawhub install kube-medic` |
| [log-dive](skills/log-dive/) | Unified log search (Loki / Elasticsearch / CloudWatch) | 0.1.1 | `clawhub install log-dive` |
| [tf-plan-review](skills/tf-plan-review/) | Terraform plan risk assessment & blast radius analysis | 0.1.1 | `clawhub install tf-plan-review` |

### 🚨 Incident Response

| Skill | Description | Version | Install |
|-------|-------------|---------|---------|
| [pager-triage](skills/pager-triage/) | PagerDuty incident triage & resolution workflows | 0.1.1 | `clawhub install pager-triage` |

### 🧠 Productivity

| Skill | Description | Version | Install |
|-------|-------------|---------|---------|
| [feed-diet](skills/feed-diet/) | Information diet auditor (HN, RSS/OPML analysis) | 0.1.1 | `clawhub install feed-diet` |
| [meeting-autopilot](skills/meeting-autopilot/) | Meeting transcript → action items, decisions & follow-ups | 0.1.1 | `clawhub install meeting-autopilot` |

### 🔜 Coming This Week

| Skill | Description | ETA |
|-------|-------------|-----|
| sentry-scout | Sentry error triage & stacktrace analysis | Mon–Tue |
| test-pilot | Playwright test runner & failure analyzer | Wed |
| stripe-dash | Stripe revenue intelligence (read-only) | Thu–Fri |

## Quick Start

```bash
# Install from ClawHub
clawhub install vibe-check

# Or clone and install any skill locally
git clone https://github.com/cacheforge-ai/cacheforge-skills.git
cp -r cacheforge-skills/skills/vibe-check ~/.openclaw/skills/
```

## What Makes CacheForge Skills Different

🔧 **Real CLI integrations** — wraps actual tools (`promtool`, `kubectl`, `terraform`, `pip-audit`, `cargo-audit`, `npm audit`), not prompt-only LLM wrappers that hallucinate data.

🛡️ **Safe by default** — read-only first. Every destructive action is gated by explicit user confirmation. No YOLO `kubectl delete` on your production cluster.

💬 **Discord v2 ready** — compact first response with interactive follow-up actions. Designed for OpenClaw v2026.2.14+ delivery modes across Discord, Telegram, and webchat.

🏗️ **Security hardened** — no `eval`, no `bash -c` with variable interpolation, all JSON via `jq --arg`, URL scheme validation, `set -euo pipefail` everywhere. Every script passes `bash -n` syntax checks.

📊 **Screenshot-worthy output** — scored reports, risk matrices, ASCII charts, and emoji-rich Markdown. Built to be shared.

⚡ **Battle-tested** — this entire skill suite was built, reviewed, and hardened in a single day using a multi-agent pipeline running through CacheForge. 30M+ tokens. 455 requests. 10 production skills.

## The Observability Stack

CacheForge is the **only publisher on ClawHub with a complete observability suite**:

```
┌─────────────┐  ┌──────────┐  ┌───────────────┐  ┌──────────────┐
│  prom-query  │  │ log-dive │  │ pager-triage  │  │ sentry-scout │
│   (metrics)  │  │  (logs)  │  │  (incidents)  │  │   (errors)   │
└──────┬───────┘  └────┬─────┘  └──────┬────────┘  └──────┬───────┘
       │               │               │                   │
       └───────────────┴───────────────┴───────────────────┘
                    Your AI-powered NOC
```

Query Prometheus metrics → correlate with logs → triage the PagerDuty alert → trace the Sentry error. All through your OpenClaw agent.

## Discord v2 Ready

All CacheForge skills include a **Discord v2 delivery contract** for OpenClaw v2026.2.14+:

- 📦 **Compact first response** — summary with key findings, under ~1200 chars
- 🎛️ **Component-style follow-ups** — interactive quick actions when Discord components are available
- 📋 **Graceful fallback** — numbered action list when components aren't available
- 📄 **Chunked detail** — long reports sent in ≤15 line chunks for readability

Works great on Telegram (with inline buttons), webchat, and all other OpenClaw surfaces.

## Architecture

Every CacheForge skill follows the same contract:

```
SKILL.md          → Agent-readable skill definition (frontmatter + instructions)
README.md         → Human-readable documentation
CHANGELOG.md      → Version history
SECURITY.md       → Security model and threat analysis
TESTING.md        → Test procedures and validation
scripts/          → Bash CLI wrappers (set -euo pipefail, no eval)
```

Skills are **stateless** — no databases, no background processes, no daemons. They wrap real CLI tools and APIs, adding agent intelligence on top.

## Built with CacheForge

This entire skill suite was built using a multi-agent pipeline running through [CacheForge](https://app.anvil-ai.io):

| Metric | Value |
|--------|-------|
| Total tokens | 30.6M |
| Requests | 455 |
| Model | Claude Opus 4.6 |
| Direct API cost | ~$413 |
| CacheForge cost | ~$143 |
| **Savings** | **$270 (65%)** |

CacheForge makes AI agents affordable at scale. [Learn more →](https://app.anvil-ai.io)

## Contributing

We're not accepting external contributions yet. [Open an issue](https://github.com/cacheforge-ai/cacheforge-skills/issues) to suggest a skill.

## License

[MIT](LICENSE)

---

<div align="center">

**Built with 🔥 by [CacheForge](https://app.anvil-ai.io)**

*10 skills. 30M tokens. One day. One platform.*

</div>
