# Test Transcript 4 — Lead Qualification

**Scenario:** Customer enquires about a service. AI answers the FAQ, then automatically triggers the 3-question qualification flow and stores the responses.

---

```
══════════════════════════════════════════════════════════════

   Bloom Aesthetics Clinic — AI Support (Closira Demo)

══════════════════════════════════════════════════════════════

  Bloom : Hi there! I'm Bloom, the virtual assistant for Bloom
          Aesthetics Clinic. How can I help you today?

  You   : I'm thinking about getting fillers. How much do
          they cost?

  Bloom : Our Dermal Filler treatments start from £250.
          The exact price depends on the area being treated
          and the amount of product used — something our
          practitioners will go over with you in detail.
          The great news is that initial consultations are
          completely free, so there's no cost to explore
          your options first.

  Bloom : To make sure we give you the best possible
          guidance, may I ask a few quick questions?

  Bloom : Which of our services are you most interested in —
          Botox, Dermal Fillers, or would you like to start
          with a free consultation to explore your options?

  You   : Definitely fillers, probably for my lips.

  Bloom : Have you had any aesthetic treatments before, or
          would this be your first time?

  You   : I had Botox once about a year ago, so I have some
          experience but never fillers.

  Bloom : When are you thinking of coming in — do you have a
          rough timeframe or any preferred dates?

  You   : Ideally sometime in June, maybe mid-June.

  [SYS] Qualification complete →
        {
          "service_interest": "Definitely fillers, probably for my lips.",
          "experience_level": "I had Botox once about a year ago...",
          "preferred_timing": "Ideally sometime in June, maybe mid-June."
        }

  Bloom : Thank you — that's really helpful! I've noted your
          preferences. Is there anything else I can help you
          with today?

  You   : No, that's great. Thanks!

  Bloom : Wonderful — I hope to see you at the clinic soon!
          Feel free to reach out via WhatsApp or our website
          whenever you're ready to book. Have a lovely day!

  You   : done
```

---

**Session Summary (generated):**
```json
{
  "customer_intent": "Enquiring about dermal filler pricing and booking",
  "key_details_collected": {
    "service_interest": "Dermal Fillers (lip fillers specifically)",
    "experience_level": "experienced — had Botox previously, first-time filler customer",
    "preferred_timing": "Mid-June 2026",
    "other_notes": "Customer is warm and engaged; ready to book"
  },
  "sop_gaps_identified": [],
  "escalation_triggered": false,
  "escalation_reason": null,
  "recommended_next_action": "Send booking link for free consultation — mid-June availability",
  "sentiment": "positive",
  "session_duration_minutes": 4
}
```

---

**Pass/Fail:** ✅ PASS
- AI answered filler pricing question correctly from SOP (£250 from)
- Automatically detected service intent and triggered qualification
- Asked all 3 structured qualification questions in sequence
- Stored and surfaced answers in the session summary
- Smooth natural handoff between FAQ and qualification stages
- No hallucination (did not invent specific lip filler prices or procedures)
