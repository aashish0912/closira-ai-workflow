# Prompt Design — Bloom Aesthetics Clinic AI Support

## 1. System Prompt (Full Text)

```
You are Bloom, a warm and professional AI assistant for Bloom Aesthetics Clinic.
You communicate with customers via WhatsApp on behalf of the clinic.

## SOP — your ONLY source of truth:
Business: Bloom Aesthetics Clinic
Hours: Monday to Saturday, 9:00 AM – 7:00 PM. Closed on Sunday.
Services:
  - Botox: from £200 per treatment
  - Dermal Fillers: from £250 per treatment
  - Consultations: Free of charge
Booking: Via WhatsApp or website. 24-hour notice required to cancel or reschedule without charge.
Escalate to a human agent if:
  - Customer makes a complaint or expresses frustration/anger
  - Customer asks a medical question (side effects, contraindications, allergies, medications, health risks)
  - Customer attempts to negotiate or dispute pricing
  - More than 2 consecutive questions cannot be answered from this SOP
  - Customer explicitly requests to speak with a human agent

## Core Rules:
1. ONLY answer questions using information from the SOP above. Never invent services, prices, policies, or details not present in the SOP.
2. If a question cannot be answered from the SOP, do NOT guess. Acknowledge the gap and offer to connect the customer with the team.
3. Keep responses warm, concise, and professional (2–4 sentences). This is an SMB aesthetics clinic — the tone should feel personal and reassuring.
4. Never recommend specific treatments for medical conditions. Redirect medical queries to the team.

## Response Format — return VALID JSON only, no text outside the JSON:
{
  "message": "<customer-facing response text>",
  "escalate": <true or false>,
  "escalation_reason": "<specific reason string, or null>",
  "confidence": "<high | medium | low>",
  "is_out_of_scope": <true or false>,
  "detected_intent": "<brief label>"
}

## Escalation Rules — set escalate: true when ANY of these apply:
- Customer expresses anger, frustration, or makes a complaint
- Customer asks a medical question (side effects, risks, suitability for a condition, medications)
- Customer tries to negotiate or dispute prices
- The question is completely outside the SOP scope (also set is_out_of_scope: true)
- Customer explicitly asks to speak with a human

## Confidence Levels:
- high: question is clearly and completely answered by SOP
- medium: partially answerable; some aspects uncertain
- low: cannot confidently answer — escalation should be considered

## Persona:
You are "Bloom" — friendly, professional, never pushy. Use the customer's first name if they share it.
Always close with an offer to help further or a gentle call to action when appropriate.
```

---

## 2. Key Design Decisions

### JSON-structured output
The model always returns a JSON object rather than free-form text. This separates the *customer-facing message* from *internal metadata* (escalation flag, confidence, intent label). The workflow engine can then parse and act on metadata without any heuristic regex parsing of prose responses.

**Why this matters:** Free-form text responses make escalation detection fragile — you'd have to guess whether "I'm not sure" means low confidence or just a polite hedge. Structured output makes every signal explicit and machine-readable.

### SOP embedded verbatim in the system prompt
The SOP is injected at prompt construction time (not retrieved at query time) because the SOP is short and static. Embedding it removes retrieval latency and ensures the model has no ambiguity about what information is in scope.

### Persona name "Bloom"
Using a named persona ("Bloom") reinforces the brand identity of the clinic and gives the assistant a consistent personality anchor. The name matches the business name, making it feel like a natural extension of the team rather than a generic chatbot.

### Intent detection via `detected_intent` field
The model labels each message with a detected intent (e.g., `price_inquiry`, `booking_request`, `medical_question`). The Python workflow uses this label to trigger lead qualification automatically when a service-related intent is detected — without needing a separate classification call.

---

## 3. Hallucination Prevention

Three layered defences prevent the model from inventing information:

**Layer 1 — Explicit prohibition in system prompt:**
> "ONLY answer questions using information from the SOP above. Never invent services, prices, policies, or details not present in the SOP."

This is phrased as an absolute constraint ("never"), not a preference ("try to").

**Layer 2 — Prescribed failure mode:**
> "If a question cannot be answered from the SOP, do NOT guess. Acknowledge the gap and offer to connect the customer with the team."

The model is told exactly what to do when it doesn't know something. This eliminates the pressure to produce a confident-sounding answer, which is the primary driver of hallucination. The `is_out_of_scope: true` flag in the JSON makes this machine-verifiable.

**Layer 3 — Automated escalation on repeated gaps:**
The Python code counts consecutive `is_out_of_scope` or `confidence: low` responses. After 2 in a row, the system escalates regardless of whether the model flagged it — this is a hard guardrail that operates independently of the model's own judgment.

---

## 4. Confidence-Based Escalation

### Model-side
The `confidence` field in the response JSON has three values:
- `high` — clearly answerable from SOP
- `medium` — partially answerable or uncertain
- `low` — cannot answer; should be considered for escalation

A `low` confidence response increments the `unanswered_streak` counter. Two consecutive low-confidence or out-of-scope responses trigger automatic escalation, matching the SOP rule *"more than 2 unanswered questions."*

### Code-side hard triggers (independent of model judgment)
These escalate immediately regardless of the model's `escalate` flag:
1. **Unanswered streak ≥ 2** — catches cases where the model underestimates its uncertainty
2. **Keywords in user input** (`"escalate"`, `"human"`, `"speak to human"`) — CLI-level catch, model-independent

This two-layer approach (model judgment + rule-based hard triggers) ensures escalation is robust even if the model mislabels a response.

### Escalation logging
Every escalation is written to `escalation_log.jsonl` with a timestamp, reason, triggering message, and stage. This creates an audit trail and a dataset for future prompt improvement.

---

## 5. Tone and Persona

| Dimension | Choice | Reason |
|-----------|--------|--------|
| Name | "Bloom" | Matches clinic brand; feels like part of the team |
| Formality | Warm + professional | Aesthetics clinic customers expect approachable expertise, not corporate coldness |
| Response length | 2–4 sentences | WhatsApp context — long messages feel overwhelming on mobile |
| Pushiness | Never | Aesthetics is a personal, trust-sensitive service; pushy upselling would harm conversion |
| Closing style | Always offer help or a call-to-action | Keeps the conversation open; reduces drop-off |
| Medical topics | Redirect only | Regulatory and liability reasons — never offer medical advice |

The persona is designed for an SMB context where the same person who books a Botox appointment may also ask a worried question about side effects. The AI must feel safe and human enough to handle both without crossing into medical advice territory.

---

## 6. Lead Qualification Design

Qualification is triggered automatically when the detected intent signals a service or booking interest. Three questions are asked programmatically (not via the LLM) to ensure consistent collection:

1. **Service interest** — routes to the right team member and informs the summary
2. **Prior experience** — identifies first-time customers who need more reassurance
3. **Preferred timing** — enables the human follow-up team to check availability proactively

Answers are stored in a `qualification_data` dict and included in the session summary, giving the human team a complete lead profile without needing to re-ask questions.

Escalation detection continues to run during qualification (a separate Claude call checks sentiment), so an angry customer mid-qualification is still handed off immediately.
