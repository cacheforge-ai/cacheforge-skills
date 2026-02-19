# Publishing CacheForge Skills (ClawHub)

This repo is a **skill pack**. ClawHub publishes **one skill folder at a time**.

Recommended product shape:
- Users install one primary skill: `cacheforge`
- The primary skill bootstraps companion skills (`cacheforge-setup`, `cacheforge-ops`, `cacheforge-stats`) when needed.

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
openclaw skills info cacheforge
openclaw skills info cacheforge-setup
openclaw skills info cacheforge-ops
openclaw skills info cacheforge-stats

# Script syntax sanity
python3 -m py_compile \
  skills/cacheforge-setup/setup.py \
  skills/cacheforge-ops/ops.py \
  skills/cacheforge-stats/dashboard.py

# Primary skill bootstrap sanity
bash skills/cacheforge/scripts/bootstrap-companions.sh
```

## Publish (Primary + Companions)

Pick one version for this release (recommended: keep all 4 skills on the same version).

```bash
cd ~/cacheforge-skill

VERSION="0.1.0"
CHANGELOG="Primary CacheForge skill with companion bootstrap and onboarding/ops/stats flow."

clawhub publish ./skills/cacheforge \
  --slug cacheforge \
  --name "CacheForge" \
  --version "$VERSION" \
  --changelog "$CHANGELOG" \
  --tags latest

# Companion skills (installed by the primary skill bootstrap)
clawhub publish ./skills/cacheforge-setup \
  --slug cacheforge-setup \
  --name "CacheForge Setup" \
  --version "$VERSION" \
  --changelog "$CHANGELOG" \
  --tags latest

clawhub publish ./skills/cacheforge-ops \
  --slug cacheforge-ops \
  --name "CacheForge Ops" \
  --version "$VERSION" \
  --changelog "$CHANGELOG" \
  --tags latest

clawhub publish ./skills/cacheforge-stats \
  --slug cacheforge-stats \
  --name "CacheForge Stats" \
  --version "$VERSION" \
  --changelog "$CHANGELOG" \
  --tags latest
```

## Verify install (user path)

```bash
mkdir -p /tmp/cf-skill-test && cd /tmp/cf-skill-test
clawhub install cacheforge

# optional explicit companion install check
for s in cacheforge-setup cacheforge-ops cacheforge-stats; do clawhub install "$s"; done
```

Or run a registry dry run for just this repo:

```bash
clawhub --workdir ~/cacheforge-skill --dir skills sync --dry-run --root ~/cacheforge-skill/skills
```
