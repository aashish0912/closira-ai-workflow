# Test Transcript 1 — In-SOP Question: Botox Prices

**Scenario:** Customer asks about Botox pricing. The AI must answer accurately from the SOP only.

---

```
══════════════════════════════════════════════════════════════

   Bloom Aesthetics Clinic — AI Support (Closira Demo)

══════════════════════════════════════════════════════════════

   Commands: 'done' → end session & view summary
             'escalate' → request a human agent

──────────────────────────────────────────────────────────────

  Bloom : Hi there! I'm Bloom, the virtual assistant for Bloom
          Aesthetics Clinic. How can I help you today?

  You   : What are your Botox prices?

  Bloom : Our Botox treatments start from £200. If you'd like
          to find out exactly what's included and which areas
          are best suited to your goals, I'd recommend booking
          a free consultation with one of our practitioners —
          it's a great way to get a personalised plan with no
          commitment.

          Would you like to know how to book, or is there
          anything else I can help with?

  You   : done
```

---

**Session Summary (generated):**
```json
{
  "customer_intent": "Enquiring about Botox pricing",
  "key_details_collected": {
    "service_interest": null,
    "experience_level": null,
    "preferred_timing": null,
    "other_notes": "Customer asked specifically about Botox price"
  },
  "sop_gaps_identified": [],
  "escalation_triggered": false,
  "escalation_reason": null,
  "recommended_next_action": "Send booking link for free consultation",
  "sentiment": "neutral",
  "session_duration_minutes": 1
}
```

---

**Pass/Fail:** ✅ PASS
- AI responded with the correct SOP price (£200 from)
- No hallucinated details (did not invent specific treatment areas, package details, or prices for individual areas)
- Offered free consultation as the natural next step
- `escalate: false`, `confidence: high`, `is_out_of_scope: false`
