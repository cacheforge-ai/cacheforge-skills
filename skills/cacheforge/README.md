# cacheforge (OpenClaw Skill)

Core configuration skill for CacheForge. Teaches OpenClaw (and any skill-aware agent) how to:

1. Add CacheForge as a `models.providers` entry (OpenAI-compatible or Anthropic Messages).
2. Provide the API key safely via environment variable or `skills.entries`.
3. Validate that requests are flowing and caching telemetry is working.

See `SKILL.md` for the full configuration reference.
