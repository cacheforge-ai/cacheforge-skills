# Publishing Skills (ClawHub)

This repo is a **skill pack**. ClawHub publishes **one skill folder at a time**.

## Public Release Set

Public release set:
- `agentic-devops`
- `context-engineer`
- `dep-audit`
- `feed-diet`
- `kube-medic`
- `log-dive`
- `meeting-autopilot`
- `pager-triage`
- `prom-query`
- `rug-checker`
- `tf-plan-review`
- `vibe-check`

## OpenClaw/ClawHub Requirements (grounded in local docs)

- Each skill folder must include a valid `SKILL.md` with single-line YAML frontmatter keys.
- `metadata` in frontmatter must be a single-line JSON object.
- Publish is one folder/slug at a time (`clawhub publish <path>`).
- Use semver on every publish.

References checked:
- `~/openclaw/docs/tools/skills.md`
- `~/openclaw/docs/tools/clawhub.md`

## Prereqs

```bash
npm i -g clawhub
clawhub login
clawhub whoami
```

## Preflight (before publish)

```bash
cd ~/cacheforge-skill

# OpenClaw eligibility + metadata sanity
openclaw skills check
for s in agentic-devops context-engineer dep-audit feed-diet kube-medic log-dive meeting-autopilot pager-triage prom-query rug-checker tf-plan-review vibe-check; do
  openclaw skills info "$s"
done

# Script syntax sanity (only where scripts exist)
python3 -m py_compile skills/context-engineer/context.py
python3 -m py_compile skills/agentic-devops/devops.py
```

## Publish Public Skills (Per-Slug)

Pick one version for this release.

```bash
cd ~/cacheforge-skill

VERSION="0.1.0"
CHANGELOG="Open-source agentic workflow and operations skills."

for s in agentic-devops context-engineer dep-audit feed-diet kube-medic log-dive meeting-autopilot pager-triage prom-query rug-checker tf-plan-review vibe-check; do
  clawhub publish "./skills/$s" \
    --slug "$s" \
    --name "$s" \
    --version "$VERSION" \
    --changelog "$CHANGELOG" \
    --tags latest
done
```

## Verify install (user path)

```bash
mkdir -p /tmp/cf-skill-test && cd /tmp/cf-skill-test
clawhub install context-engineer
clawhub install agentic-devops
clawhub install dep-audit
clawhub install log-dive
```

Or run a registry dry run for just this repo:

```bash
clawhub --workdir ~/cacheforge-skill --dir skills sync --dry-run --root ~/cacheforge-skill/skills
```
