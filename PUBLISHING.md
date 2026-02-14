# Publishing CacheForge Skills (ClawHub)

This repo is a **skill pack** (multiple skill folders). ClawHub publishes **one skill folder at a time**.

## Prereqs

```bash
npm i -g clawhub
clawhub login
clawhub whoami
```

## Publish (all 4 skills)

Pick one version for this release (recommended: keep all 4 skills on the same version).

```bash
cd ~/cacheforge-skill

VERSION="0.1.0"
CHANGELOG="Initial release: CacheForge setup + ops + stats + OpenClaw wiring."

clawhub publish ./skills/cacheforge \
  --slug cacheforge \
  --name "CacheForge" \
  --version "$VERSION" \
  --changelog "$CHANGELOG" \
  --tags latest

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

## Verify install

```bash
mkdir -p /tmp/cf-skill-test && cd /tmp/cf-skill-test
for s in cacheforge cacheforge-setup cacheforge-ops cacheforge-stats; do clawhub install "$s"; done
```

