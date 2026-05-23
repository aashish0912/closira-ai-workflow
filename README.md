# Closira AI Customer Support Workflow
### Bloom Aesthetics Clinic — Demo Implementation

A Python-based AI customer support agent built with the **Groq API (Llama 3.3 70B)**, demonstrating a four-stage agentic workflow for SMB customer communication.

---

## Demo Video

**[Watch the 7-minute walkthrough](https://github.com/aashish0912/closira-ai-workflow/releases/download/v1.0/demo-walkthrough.mp4)**

The video covers all four stages live: FAQ answering, lead qualification, escalation detection, and conversation summary generation.

---

## Features

| Stage | Description |
|-------|-------------|
| 1. FAQ Answering | Answers inbound questions strictly from the SOP — no hallucination |
| 2. Lead Qualification | Automatically triggers 3-question qualification on service interest |
| 3. Escalation Detection | Detects complaints, medical questions, low confidence, and out-of-scope queries |
| 4. Conversation Summary | Generates a structured JSON summary at session end |

---

## Project Structure

```
closira/
├── workflow.py              # Main CLI workflow
├── sop_data.json            # SOP source data for Bloom Aesthetics Clinic
├── requirements.txt
├── prompt_design.md         # Full prompt design decisions and rationale
├── README.md
├── escalation_log.jsonl     # Created at runtime — append-only escalation log
├── session_summary.json     # Created at runtime — last session summary
└── test_transcripts/
    ├── 01_in_scope_question.md
    ├── 02_out_of_scope_question.md
    ├── 03_escalation_trigger.md
    ├── 04_lead_qualification.md
    └── 05_conversation_summary.md
```

---

## Setup

### Prerequisites
- Python 3.10+
- A free Groq API key — sign up at [console.groq.com](https://console.groq.com/) (no credit card required)

### Install

```bash
# Clone or download the project
cd closira

# Create a virtual environment (recommended)
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Configure API key

Option A — `.env` file (recommended):
```bash
echo "GROQ_API_KEY=gsk_..." > .env
```

Option B — environment variable:
```bash
export GROQ_API_KEY=gsk_...    # Windows: set GROQ_API_KEY=gsk_...
```

---

## Run

```bash
python workflow.py
```

The CLI starts an interactive conversation. Type your message and press Enter.

**Special commands:**
- `done` — End the session and generate a structured summary
- `escalate` — Immediately request a human agent

---

## How It Works

### Workflow state machine

```
[Start]
   │
   ▼
[FAQ Stage] ──── service intent detected? ──── yes ──► [Qualification Stage]
   │                                                          │
   │ ◄────────────────────────────── all 3 questions done ───┘
   │
   ▼ (any stage)
[Escalation check] ──── trigger detected ──► [Escalated → exit]
   │
   ▼ (user types 'done')
[Summary Generation → exit]
```

### Response format

Every Claude call returns a JSON object:

```json
{
  "message": "customer-facing text",
  "escalate": false,
  "escalation_reason": null,
  "confidence": "high | medium | low",
  "is_out_of_scope": false,
  "detected_intent": "price_inquiry"
}
```

Every API call returns this JSON object. The Python layer reads the metadata to decide stage transitions and escalation, keeping the LLM focused only on generating good responses.

### Escalation triggers

| Trigger | Source |
|---------|--------|
| Angry sentiment / complaint | LLM (`escalate: true`) |
| Medical question | LLM (`escalate: true`) |
| Pricing negotiation | LLM (`escalate: true`) |
| Out-of-scope question | LLM (`is_out_of_scope: true`) |
| ≥2 consecutive out-of-scope | Python hard rule |
| Explicit human request | Python keyword match |

All escalations are appended to `escalation_log.jsonl` with timestamp, reason, and triggering message.

---

## SOP Data

The SOP is defined in `sop_data.json` and injected into the system prompt at startup. To adapt this workflow to a different business:

1. Edit `sop_data.json` with the new business details
2. The `SOP_TEXT` block in `workflow.py` reads from it automatically
3. Update `QUALIFICATION_QUESTIONS` in `workflow.py` if the lead qualification questions should change

---

## Trade-offs and Known Limitations

| Limitation | Details |
|------------|---------|
| Single-turn model calls | Each FAQ response is a fresh call with full message history. For very long sessions (50+ turns), token costs increase linearly. A sliding window or summarisation strategy would reduce this. |
| Qualification is rule-based | The 3 qualification questions are always asked in a fixed order. A more sophisticated version could use Claude to ask follow-up questions dynamically based on earlier answers. |
| No persistent session storage | Sessions are in-memory only; restarting the script starts a fresh conversation. Adding a session store (SQLite, Redis) would enable multi-channel continuity. |
| English only | The system prompt and persona are English-only. Multi-language support would require language detection and prompt variants. |
| No retry logic on API errors | A single API failure will use a fallback message but not retry. Production use should add exponential backoff. |
| CLI only | No web or WhatsApp integration — this is a demo. A production deployment would connect this logic to a messaging gateway (e.g., Twilio for WhatsApp). |

---

## Model Used

`llama-3.3-70b-versatile` via the Groq API (free tier — no credit card required).
