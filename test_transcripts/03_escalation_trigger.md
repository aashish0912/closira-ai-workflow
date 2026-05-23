# Test Transcript 3 — Escalation Trigger: Frustration / Complaint

**Scenario:** Customer expresses frustration about a previous appointment experience. The AI detects negative sentiment and escalates with a logged reason.

---

```
══════════════════════════════════════════════════════════════

   Bloom Aesthetics Clinic — AI Support (Closira Demo)

══════════════════════════════════════════════════════════════

  Bloom : Hi there! I'm Bloom, the virtual assistant for Bloom
          Aesthetics Clinic. How can I help you today?

  You   : I had an appointment last week and the results are
          terrible. I'm really unhappy and I want to complain.

  [SYS] ESCALATION LOGGED → Customer expressed frustration or
        made a complaint

  Bloom : I'm really sorry to hear that you're unhappy with
          your experience — that's never what we want for our
          clients, and your feedback matters greatly to us.
          I'm immediately flagging this conversation to our
          team so that a senior member can reach out to you
          personally and make this right.

  Bloom : I've flagged this conversation so one of our team
          members can follow up with you directly. We'll be
          in touch very soon!
```

---

**escalation_log.jsonl entry:**
```json
{
  "timestamp": "2026-05-23T17:15:42.331Z",
  "reason": "Customer expressed frustration or made a complaint",
  "trigger_message": "I had an appointment last week and the results are terrible. I'm really unhappy and I want to complain.",
  "stage_at_escalation": "faq"
}
```

---

**Session Summary (generated):**
```json
{
  "customer_intent": "Lodging a complaint about a previous treatment result",
  "key_details_collected": {
    "service_interest": null,
    "experience_level": "experienced",
    "preferred_timing": null,
    "other_notes": "Customer unhappy with results from a recent appointment"
  },
  "sop_gaps_identified": [],
  "escalation_triggered": true,
  "escalation_reason": "Customer expressed frustration or made a complaint",
  "recommended_next_action": "Urgent human follow-up required — complaint resolution",
  "sentiment": "negative",
  "session_duration_minutes": 1
}
```

---

**Pass/Fail:** ✅ PASS
- AI detected angry/complaint sentiment immediately on first message
- Responded empathetically without dismissing the complaint
- Escalated at once — did not attempt to resolve the complaint itself (which would be inappropriate for an AI)
- Escalation reason clearly logged with timestamp and triggering message
