<div align="center">

# ⚡ Agentic Skills

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Skills](https://img.shields.io/badge/skills-14-blue.svg)](#skills)
[![ClawHub](https://img.shields.io/badge/ClawHub-published-green.svg)](https://clawhub.com)
[![OpenClaw](https://img.shields.io/badge/OpenClaw-v2026.2.14+-purple.svg)](https://github.com/openclaw/openclaw)
[![Discord](https://img.shields.io/badge/Discord-v2%20ready-5865F2.svg)](https://discord.com)
[![Live Lab](https://img.shields.io/badge/Live%20Lab-labs.anvil--ai.io-ff6b35.svg)](https://labs.anvil-ai.io)

**Production-grade agent skills for [OpenClaw](https://github.com/openclaw/openclaw) and the [ClawHub](https://clawhub.com) marketplace.**

Built by [Anvil AI](https://labs.anvil-ai.io) — R&D enterprise for agentic infrastructure.

---

*Battle-tested on a 5-agent autonomous swarm running 24/7. If it ships here, it survived production first.*

</div>

---

## Skills

### 🔍 Code Quality & Security

| Skill | Description | Version | Install |
|-------|-------------|---------|---------|
| [vibe-check](skills/vibe-check) | Code quality auditor for risky AI-generated patterns. Catches what linters miss. | 0.1.2 | `clawhub install vibe-check` |
| [dep-audit](skills/dep-audit) | Dependency vulnerability scanner across npm, pip, Cargo, and Go. | 0.1.4 | `clawhub install dep-audit` |
| [rug-checker](skills/rug-checker) | Solana token risk analysis with visual scoring. Trust, but verify. | 0.1.4 | `clawhub install rug-checker` |

### 📡 Observability & Infrastructure

| Skill | Description | Version | Install |
|-------|-------------|---------|---------|
| [prom-query](skills/prom-query) | Prometheus metrics query and alert interpreter. | 1.0.2 | `clawhub install prom-query` |
| [kube-medic](skills/kube-medic) | Kubernetes cluster triage and diagnostics. First responder for your pods. | 1.0.2 | `clawhub install kube-medic` |
| [log-dive](skills/log-dive) | Unified log investigation (Loki, Elasticsearch, CloudWatch). | 0.1.2 | `clawhub install log-dive` |
| [swarm-self-heal](skills/swarm-self-heal) | Swarm watchdog for gateway/channel/lane liveness with bounded recovery receipts. | 0.1.1 | `clawhub install swarm-self-heal` |
| [tf-plan-review](skills/tf-plan-review) | Terraform plan risk assessment before apply. | 0.1.2 | `clawhub install tf-plan-review` |

### 🚨 Incident Response

| Skill | Description | Version | Install |
|-------|-------------|---------|---------|
| [pager-triage](skills/pager-triage) | PagerDuty incident triage and on-call workflow support. | 0.1.2 | `clawhub install pager-triage` |

### 🧠 Productivity

| Skill | Description | Version | Install |
|-------|-------------|---------|---------|
| [feed-diet](skills/feed-diet) | Information-diet analysis across HN and RSS/OPML. Cut the noise. | 0.1.2 | `clawhub install feed-diet` |
| [meeting-autopilot](skills/meeting-autopilot) | Transcript-to-action pipeline — decisions, owners, follow-ups. No more "what did we decide?" | 0.1.2 | `clawhub install meeting-autopilot` |

### 🛠️ Core Engineering

| Skill | Description | Version | Install |
|-------|-------------|---------|---------|
| [agentic-devops](skills/agentic-devops) | Docker, process, log, and health operations toolkit. | 1.0.1 | `clawhub install agentic-devops` |
| [context-engineer](skills/context-engineer) | Context-window analysis and optimization workflows. | 1.0.1 | `clawhub install context-engineer` |
| [continuity-kernel](skills/continuity-kernel) | Fail-open continuity kernel with deterministic runtime contracts and shadow eval receipts. | 0.2.0 | `clawhub install continuity-kernel` |

---

## Quick Install

```bash
clawhub install agentic-devops
clawhub install context-engineer
clawhub install continuity-kernel
clawhub install log-dive
clawhub install dep-audit
```

## Adding a New Skill

New skills must be categorized into an existing section above (or propose a new category with justification). Every skill needs:

- A folder under `skills/<skill-name>/`
- A `SKILL.md` with frontmatter (name, description, license, metadata)
- A row in the appropriate category table in this README
- Version tracking and a CHANGELOG entry

Follow the existing format exactly — folder layout, metadata schema, table style.

## Links

- Lab: [labs.anvil-ai.io](https://labs.anvil-ai.io) — live demos, proposals, and community voting
- GitHub: [cacheforge-ai/cacheforge-skills](https://github.com/cacheforge-ai/cacheforge-skills)
- ClawHub: [clawhub.com](https://clawhub.com)

## License

[MIT](LICENSE)
