# Publishing Skills (ClawHub)

This repo is a **skill pack**. ClawHub publishes **one skill folder at a time**.

## Public Release Set

Public release set is all non-CacheForge slugs in `skills/`:
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

Private/internal skills in `skills/cacheforge*` are intentionally depublished and must stay out of public releases.

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
for s in $(ls skills | grep -v '^cacheforge'); do
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

for s in $(ls skills | grep -v '^cacheforge'); do
  clawhub publish "./skills/$s" \
    --slug "$s" \
    --name "$s" \
    --version "$VERSION" \
    --changelog "$CHANGELOG" \
    --tags latest
done
```

## Do Not Publish

Do not publish these slugs from this repo:
- `cacheforge`
- `cacheforge-setup`
- `cacheforge-ops`
- `cacheforge-stats`
- `cacheforge-bench`

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
