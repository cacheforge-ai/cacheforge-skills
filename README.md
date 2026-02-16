<div align="center">

# 🔥 CacheForge Agent Skills

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Skills](https://img.shields.io/badge/skills-10-blue.svg)](#skills)
[![ClawHub](https://img.shields.io/badge/ClawHub-published-green.svg)](https://clawhub.com)
[![OpenClaw](https://img.shields.io/badge/OpenClaw-v2026.2.14+-purple.svg)](https://github.com/moltbot/moltbot)

**Production-grade Agent Skills for [OpenClaw](https://github.com/moltbot/moltbot) and the [ClawHub](https://clawhub.com) marketplace.**

Built by [CacheForge](https://app.anvil-ai.io) — making AI agents affordable, powerful, and production-ready.

---

*Real CLI integrations. Safe by default. Discord v2 ready.*

</div>

## Skills

| Skill | Description | Status | Version |
|-------|-------------|--------|---------|
| [vibe-check](skills/vibe-check/) | Code quality auditor — catches "vibe coding" sins | ✅ Published | 0.1.1 |
| [rug-checker](skills/rug-checker/) | Solana token rug-pull risk analysis | ✅ Published | 0.1.3 |
| [dep-audit](skills/dep-audit/) | Dependency vulnerability scanner (5 ecosystems) | ✅ Published | 0.1.3 |
| [prom-query](skills/prom-query/) | Prometheus metrics query & alert interpreter | ✅ Published | 1.0.1 |
| [kube-medic](skills/kube-medic/) | Kubernetes cluster triage & pod autopsy | 🧪 Beta | 0.1.0 |
| [log-dive](skills/log-dive/) | Unified log search (Loki / Elasticsearch / CloudWatch) | 🧪 Beta | 0.1.0 |
| [tf-plan-review](skills/tf-plan-review/) | Terraform plan risk assessment | 🧪 Beta | 0.1.0 |
| [pager-triage](skills/pager-triage/) | PagerDuty incident triage & runbook automation | 🧪 Beta | 0.1.0 |
| [feed-diet](skills/feed-diet/) | Information diet auditor (HN, RSS/OPML) | 🧪 Beta | 0.1.0 |
| [meeting-autopilot](skills/meeting-autopilot/) | Meeting transcript → action items & follow-ups | 🧪 Beta | 0.1.0 |

## Quick Start

```bash
# Install from ClawHub (published skills)
clawhub install vibe-check
clawhub install rug-checker
clawhub install dep-audit
clawhub install prom-query

# Or clone and install any skill locally
git clone https://github.com/cacheforge-ai/cacheforge-skills.git
cp -r cacheforge-skills/skills/vibe-check ~/.openclaw/skills/
```

## What Makes CacheForge Skills Different

🔧 **Real CLI integrations** — wraps actual tools (`promtool`, `kubectl`, `terraform`, `pip-audit`, `cargo-audit`, `npm audit`), not prompt-only LLM wrappers that hallucinate vulnerability data.

🛡️ **Safe by default** — read-only first. Every destructive action is gated by explicit user confirmation. No YOLO `kubectl delete` on your production cluster.

💬 **Discord v2 ready** — compact, scannable output with interactive follow-ups. Designed for OpenClaw v2026.2.14+ delivery modes.

🏗️ **Production tested** — built by a 40-year engineering veteran for the workflows that actually matter at 3am when PagerDuty goes off.

📊 **Beautiful output** — scored reports, risk matrices, ASCII charts, and emoji-rich Markdown designed to be screenshot-worthy and share-worthy.

## The Observability Stack

CacheForge is building the **only complete observability suite** on ClawHub:

```
┌─────────────┐  ┌──────────┐  ┌───────────────┐  ┌──────────────┐
│  prom-query  │  │ log-dive │  │ pager-triage  │  │ sentry-scout │
│   (metrics)  │  │  (logs)  │  │  (incidents)  │  │   (errors)   │
└──────┬───────┘  └────┬─────┘  └──────┬────────┘  └──────┬───────┘
       │               │               │                   │
       └───────────────┴───────────────┴───────────────────┘
                    Your AI-powered NOC
```

Query Prometheus metrics → correlate with logs → triage the PagerDuty alert → trace the Sentry error. All from one agent.

*`sentry-scout` coming soon.*

## Skill Categories

### 🔍 Code Quality & Security
- **vibe-check** — Audits code for AI-generated quality issues, anti-patterns, and "vibe coding" sins
- **dep-audit** — Scans dependencies across Python, Node.js, Rust, Go, and Ruby for known vulnerabilities
- **rug-checker** — Analyzes Solana tokens for rug-pull risk using on-chain data

### 📡 Observability & Infrastructure
- **prom-query** — Query Prometheus/Thanos, interpret metrics, explain firing alerts
- **log-dive** — Search logs across Loki, Elasticsearch, and CloudWatch with natural language
- **kube-medic** — Triage Kubernetes clusters: crashlooping pods, resource pressure, failed deployments
- **tf-plan-review** — Review Terraform plans for security risks, cost impact, and blast radius

### 🚨 Incident Response
- **pager-triage** — Pull PagerDuty incidents, correlate with runbooks, suggest resolution steps

### 🧠 Productivity
- **feed-diet** — Audit your information diet: analyze HN activity, RSS feeds, content consumption patterns
- **meeting-autopilot** — Transform meeting transcripts into structured action items, decisions, and follow-ups

## Architecture

Every CacheForge skill follows the same contract:

```
SKILL.md          → Agent-readable skill definition (tools, permissions, prompts)
README.md         → Human-readable documentation
CHANGELOG.md      → Version history
SECURITY.md       → Security model, threat analysis, data handling
TESTING.md        → Test procedures and validation
scripts/          → CLI wrappers and helper scripts
```

Skills are **stateless** — no databases, no background processes, no daemon. They wrap existing CLI tools and APIs, adding intelligence on top.

## Contributing

We're not accepting external contributions yet, but we'd love to hear what skills you want built. [Open an issue](https://github.com/cacheforge-ai/cacheforge-skills/issues) with your idea.

## License

[MIT](LICENSE) — use these skills however you want.

## Links

- 🏪 [ClawHub Marketplace](https://clawhub.com)
- 🔥 [CacheForge](https://app.anvil-ai.io)
- 🐙 [OpenClaw](https://github.com/moltbot/moltbot)

---

<div align="center">

**Built with 🔥 by [CacheForge](https://app.anvil-ai.io)**

*Making AI agents affordable, powerful, and production-ready.*

</div>
