<div align="center">

# ⚡ Agentic Skills

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Skills](https://img.shields.io/badge/skills-13-blue.svg)](#skills)
[![ClawHub](https://img.shields.io/badge/ClawHub-published-green.svg)](https://clawhub.com)
[![OpenClaw](https://img.shields.io/badge/OpenClaw-v2026.2.14+-purple.svg)](https://github.com/moltbot/moltbot)

**SOTA agent skills for [OpenClaw](https://github.com/moltbot/moltbot) — built for production, not demos.**

_Observability. Security. Code quality. Incident response. Operator productivity._
_Real CLI integrations. Safe by default. Ship-grade or don't ship._

Built by [Anvil AI](https://anvil-ai.io) · Published on [ClawHub](https://clawhub.com)

</div>

---

## Skills

### 🔍 Code Quality & Security

| Skill | Description | Version | Install |
|-------|-------------|---------|---------|
| [vibe-check](skills/vibe-check) | Code quality auditor for risky AI-generated patterns. Catches what linters miss. | 0.1.1 | `clawhub install vibe-check` |
| [dep-audit](skills/dep-audit) | Dependency vulnerability scanner across npm, pip, Cargo, and Go. | 0.1.3 | `clawhub install dep-audit` |
| [rug-checker](skills/rug-checker) | Solana token risk analysis with visual scoring. Trust, but verify. | 0.1.3 | `clawhub install rug-checker` |

### 📡 Observability & Infrastructure

| Skill | Description | Version | Install |
|-------|-------------|---------|---------|
| [prom-query](skills/prom-query) | Prometheus metrics query and alert interpreter. | 1.0.1 | `clawhub install prom-query` |
| [kube-medic](skills/kube-medic) | Kubernetes cluster triage and diagnostics. First responder for your pods. | 1.0.1 | `clawhub install kube-medic` |
| [log-dive](skills/log-dive) | Unified log investigation — Loki, Elasticsearch, CloudWatch. One skill, every backend. | 0.1.1 | `clawhub install log-dive` |
| [tf-plan-review](skills/tf-plan-review) | Terraform plan risk assessment before you hit apply and regret it. | 0.1.1 | `clawhub install tf-plan-review` |

### 🚨 Incident Response

| Skill | Description | Version | Install |
|-------|-------------|---------|---------|
| [pager-triage](skills/pager-triage) | PagerDuty incident triage and on-call workflow support. 3 AM just got easier. | 0.1.1 | `clawhub install pager-triage` |
| [swarm-self-heal](skills/swarm-self-heal) | Swarm reliability watchdog — gateway, channel, and lane health with bounded recovery. Your agents watch themselves. | 0.1.0 | `clawhub install swarm-self-heal` |

### 🧠 Productivity

| Skill | Description | Version | Install |
|-------|-------------|---------|---------|
| [feed-diet](skills/feed-diet) | Information-diet analysis across HN and RSS/OPML. Cut the noise. | 0.1.1 | `clawhub install feed-diet` |
| [meeting-autopilot](skills/meeting-autopilot) | Transcript-to-action pipeline — decisions, owners, follow-ups. No more "what did we decide?" | 0.1.1 | `clawhub install meeting-autopilot` |

### 🛠️ Core Engineering

| Skill | Description | Version | Install |
|-------|-------------|---------|---------|
| [agentic-devops](skills/agentic-devops) | Docker, process, log, and health operations toolkit. The basics, done right. | 1.0.0 | `clawhub install agentic-devops` |
| [context-engineer](skills/context-engineer) | Context-window analysis and optimization workflows. Know what your agent actually sees. | 1.0.0 | `clawhub install context-engineer` |

---

## Quick Start

```bash
clawhub install agentic-devops    # operator essentials
clawhub install dep-audit         # supply-chain hygiene
clawhub install log-dive          # unified log investigation
clawhub install vibe-check        # catch AI-generated footguns
```

## Adding a New Skill

New skills must be categorized into an existing section above (or propose a new category with justification). Every skill needs:

- A folder under `skills/<skill-name>/`
- A `SKILL.md` with frontmatter (name, description, license, metadata)
- A row in the appropriate category table in this README
- Version tracking and a CHANGELOG entry

Follow the existing format exactly — folder layout, metadata schema, table style.

## Links

- **Anvil AI**: [anvil-ai.io](https://anvil-ai.io)
- **ClawHub**: [clawhub.com](https://clawhub.com)
- **OpenClaw**: [github.com/moltbot/moltbot](https://github.com/moltbot/moltbot)
- **This repo**: [cacheforge-ai/cacheforge-skills](https://github.com/cacheforge-ai/cacheforge-skills)

## License

[MIT](LICENSE)
