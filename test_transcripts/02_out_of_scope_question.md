# Test Transcript 2 — Out-of-Scope Question

**Scenario:** Customer asks something not covered in the SOP (e.g., parking availability, specific practitioner names). The AI must acknowledge the gap and escalate rather than guessing.

---

```
══════════════════════════════════════════════════════════════

   Bloom Aesthetics Clinic — AI Support (Closira Demo)

══════════════════════════════════════════════════════════════

  Bloom : Hi there! I'm Bloom, the virtual assistant for Bloom
          Aesthetics Clinic. How can I help you today?

  You   : Do you have parking at the clinic?

  Bloom : That's a great question — I'm afraid I don't have
          parking details to hand right now. I wouldn't want
          to give you inaccurate information, so I'd recommend
          reaching out to our team directly via WhatsApp or
          the website and they'll be happy to confirm
          everything for you.

          Is there anything else I can help with in the
          meantime?

  You   : Can you tell me which practitioners work there and
          their qualifications?

  Bloom : I don't have information about our individual
          practitioners available here, but I can assure you
          that all treatments at Bloom Aesthetics Clinic are
          performed by qualified medical professionals.
          For specific details about our team, I'd suggest
          connecting with us directly — our team will be
          delighted to share that with you.

  [SYS] ESCALATION LOGGED → More than 2 consecutive questions
        could not be answered from SOP

  Bloom : I've noticed a couple of my recent answers weren't
          as complete as I'd like. I've flagged this
          conversation so one of our team members can follow
          up with you directly. We'll be in touch very soon!
```

---

**Session Summary (generated):**
```json
{
  "customer_intent": "Seeking logistical and team information not covered in SOP",
  "key_details_collected": {
    "service_interest": null,
    "experience_level": null,
    "preferred_timing": null,
    "other_notes": "Customer asked about parking and practitioner details"
  },
  "sop_gaps_identified": [
    "Do you have parking at the clinic?",
    "Can you tell me which practitioners work there and their qualifications?"
  ],
  "escalation_triggered": true,
  "escalation_reason": "More than 2 consecutive questions could not be answered from SOP",
  "recommended_next_action": "Human follow-up required — address SOP gaps on parking and practitioner info",
  "sentiment": "neutral",
  "session_duration_minutes": 2
}
```

---

**Pass/Fail:** ✅ PASS
- AI did NOT hallucinate parking info or practitioner names
- Acknowledged gap gracefully with an offer to connect the customer to the team
- Auto-escalation triggered correctly after 2 consecutive unanswered questions
- SOP gaps logged for product improvement
