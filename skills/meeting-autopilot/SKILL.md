---
name: meeting-autopilot
description: >
  Turn meeting transcripts into operational outputs — action items, decisions,
  follow-up email drafts, and ticket drafts. Not a summarizer. An operator.
  Accepts VTT, SRT, or plain text. Multi-pass LLM extraction.
version: 0.1.0
author: cacheforge
tags: [meetings, productivity, action-items, email-drafts, transcripts, operations]
---

# ✈️ Meeting Autopilot

Turn meeting transcripts into structured operational outputs — NOT just summaries.

## Activation

This skill activates when the user mentions:
- "meeting transcript", "meeting notes", "meeting autopilot"
- "action items from meeting", "meeting follow-up"
- "process this transcript", "analyze this meeting"
- "extract decisions from meeting", "meeting email draft"
- Uploading or pasting a VTT, SRT, or text transcript

## Permissions

```yaml
permissions:
  exec: true          # Run extraction scripts
  read: true          # Read transcript files
  write: true         # Save history and reports
  network: true       # LLM API calls (Anthropic or OpenAI)
```

## Requirements

- **bash**, **jq**, **python3**, **curl** (typically pre-installed)
- **ANTHROPIC_API_KEY** or **OPENAI_API_KEY** environment variable

## Agent Workflow

### Step 1: Get the Transcript

Ask the user for their meeting transcript. Accept any of:
- A **file path** to a VTT, SRT, or TXT file
- **Pasted text** directly in the conversation
- A **file upload**

The skill auto-detects the format (VTT, SRT, or plain text).

**Important:** This skill does NOT do audio transcription. If the user has an audio/video file, suggest they use:
- Zoom/Google Meet/Teams built-in transcription
- Otter.ai or Fireflies.ai for recording + transcription
- `whisper.cpp` for local transcription

### Step 2: Get Optional Context

Ask for (but don't require):
- **Meeting title** — helps with email subject lines and report headers
- If not provided, the skill derives it from the filename or uses "Meeting [date]"

### Step 3: Run the Autopilot

Save the transcript to a temporary file if pasted, then run:

```bash
bash "$SKILL_DIR/scripts/meeting-autopilot.sh" <transcript_file> --title "Meeting Title"
```

Or from stdin:
```bash
echo "$TRANSCRIPT" | bash "$SKILL_DIR/scripts/meeting-autopilot.sh" - --title "Meeting Title"
```

The script handles all three passes automatically:
1. **Parse** — normalize the transcript format
2. **Extract** — pull out decisions, action items, questions via LLM
3. **Generate** — create email drafts, ticket drafts, beautiful report

### Step 4: Present the Report

The script outputs a complete Markdown report to stdout. Present it directly — the formatting is designed to look great in Slack, email, or any Markdown renderer.

The report includes:
- 📊 Overview table (counts by category)
- ✅ Decisions with rationale
- 📋 Action items table (owner, deadline, status)
- ❓ Open questions
- 🅿️ Parking lot items
- 📧 Follow-up email draft(s) — ready to send
- 🎫 Ticket/issue drafts — ready to file

### Step 5: Offer Next Steps

After presenting the report, offer:
1. "Want me to refine any of the email drafts?"
2. "Should I adjust any action item assignments?"
3. "Want to save this report to a file?"
4. "I can also process another meeting — transcripts from different meetings build up a tracking history."

### Error Handling

| Situation | Behavior |
|-----------|----------|
| No API key set | Print branded error with setup instructions |
| Transcript too short (<20 chars) | Suggest pasting more content or checking file path |
| Empty LLM response | Report API issue, suggest checking key/network |
| No items extracted | Report "meeting may not have had actionable content" — still show key points if any |
| Unsupported file format | Suggest --format txt to force plain text parsing |

### Notes for the Agent

- **The report is the star.** Present it in full. Don't summarize the summary.
- **Follow-up emails are the WOW moment.** Highlight them — they're ready to copy and send.
- **Be proactive:** After the report, suggest specific improvements based on what was found.
- **Cross-meeting tracking:** Items are automatically saved to `~/.meeting-autopilot/history/`. Mention this — it's a preview of the v1.1 feature that tracks commitments across meetings.
- If the transcript has no speaker labels, mention that adding "Speaker: text" format improves attribution accuracy.

## References

- `scripts/meeting-autopilot.sh` — Main orchestrator (the only entry point you need)
- `scripts/parse-transcript.sh` — Transcript parser (VTT/SRT/TXT → JSONL)
- `scripts/extract-items.sh` — LLM extraction + classification
- `scripts/generate-outputs.sh` — Operational output generation + report formatting
