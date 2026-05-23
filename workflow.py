#!/usr/bin/env python3
"""
Closira AI Customer Support Workflow
Business: Bloom Aesthetics Clinic
Four stages: FAQ Answering → Lead Qualification → (Escalation Detection throughout) → Conversation Summary
"""

import os
import sys
import json
from datetime import datetime

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stdin.reconfigure(encoding="utf-8")
from typing import Optional

from groq import Groq
from dotenv import load_dotenv

load_dotenv()

# ─── SOP ─────────────────────────────────────────────────────────────────────

with open(os.path.join(os.path.dirname(__file__), "sop_data.json")) as _f:
    SOP = json.load(_f)

SOP_TEXT = f"""
Business: {SOP['business']}
Hours: {SOP['hours']['days']}, {SOP['hours']['open']} – {SOP['hours']['close']}. Closed on {', '.join(SOP['hours']['closed_days'])}.
Services:
  - Botox: from £{SOP['services'][0]['price_from']} per treatment
  - Dermal Fillers: from £{SOP['services'][1]['price_from']} per treatment
  - Consultations: Free of charge
Booking: Via {' or '.join(SOP['booking']['channels'])}. {SOP['booking']['cancellation_policy']}
Escalate to a human agent if:
  - Customer makes a complaint or expresses frustration/anger
  - Customer asks a medical question (side effects, contraindications, allergies, medications, health risks)
  - Customer attempts to negotiate or dispute pricing
  - More than 2 consecutive questions cannot be answered from this SOP
  - Customer explicitly requests to speak with a human agent
""".strip()

QUALIFICATION_QUESTIONS = [
    "Which of our services are you most interested in — Botox, Dermal Fillers, or would you like to start with a free consultation to explore your options?",
    "Have you had any aesthetic treatments before, or would this be your first time?",
    "When are you thinking of coming in — do you have a rough timeframe or any preferred dates?",
]

QUALIFICATION_KEYS = ["service_interest", "experience_level", "preferred_timing"]


# ─── Stage constants ──────────────────────────────────────────────────────────

class Stage:
    FAQ = "faq"
    QUALIFICATION = "qualification"
    ESCALATED = "escalated"
    ENDED = "ended"


# ─── Prompts ──────────────────────────────────────────────────────────────────

SYSTEM_PROMPT = f"""You are Bloom, a warm and professional AI assistant for Bloom Aesthetics Clinic.
You communicate with customers via WhatsApp on behalf of the clinic.

## SOP — your ONLY source of truth:
{SOP_TEXT}

## Core Rules:
1. ONLY answer questions using information from the SOP above. Never invent services, prices, policies, or details not present in the SOP.
2. If a question cannot be answered from the SOP, do NOT guess. Acknowledge the gap and offer to connect the customer with the team.
3. Keep responses warm, concise, and professional (2–4 sentences). This is an SMB aesthetics clinic — the tone should feel personal and reassuring.
4. Never recommend specific treatments for medical conditions. Redirect medical queries to the team.

## Response Format — return VALID JSON only, no text outside the JSON:
{{
  "message": "<customer-facing response text>",
  "escalate": <true or false>,
  "escalation_reason": "<specific reason string, or null>",
  "confidence": "<high | medium | low>",
  "is_out_of_scope": <true or false>,
  "detected_intent": "<brief label, e.g. price_inquiry, booking_request, complaint, medical_question>"
}}

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
"""

SUMMARY_SYSTEM = """You generate structured end-of-session summaries for an AI customer support system.
Return ONLY valid JSON — no prose outside the JSON block."""

SUMMARY_USER_TEMPLATE = """Generate a structured summary for this customer support session.

Conversation transcript:
{transcript}

Qualification data collected: {qualification_data}
SOP gaps (questions that could not be answered): {sop_gaps}
Escalation triggered: {escalated}
Escalation reason: {escalation_reason}
Session duration: {duration} minutes

Return this exact JSON structure:
{{
  "customer_intent": "<primary reason the customer contacted the clinic>",
  "key_details_collected": {{
    "service_interest": "<service or null>",
    "experience_level": "<first-time | experienced | null>",
    "preferred_timing": "<timing string or null>",
    "other_notes": "<any other notable detail or null>"
  }},
  "sop_gaps_identified": ["<list of questions the SOP could not answer — empty list if none>"],
  "escalation_triggered": <true or false>,
  "escalation_reason": "<reason or null>",
  "recommended_next_action": "<e.g., Send booking link, Human follow-up required, Book free consultation>",
  "sentiment": "<positive | neutral | negative>",
  "session_duration_minutes": {duration}
}}"""


# ─── Groq client ─────────────────────────────────────────────────────────────

_client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
MODEL = "llama-3.3-70b-versatile"


def _call_llm(messages: list[dict], system: str) -> dict:
    """Call Groq and parse JSON response. `messages` uses role/content dicts."""
    full_messages = [{"role": "system", "content": system}] + messages
    response = _client.chat.completions.create(
        model=MODEL,
        messages=full_messages,
        max_tokens=1024,
        temperature=0.2,
    )
    raw = response.choices[0].message.content.strip()
    if raw.startswith("```"):
        parts = raw.split("```")
        raw = parts[1]
        if raw.startswith("json"):
            raw = raw[4:]
    return json.loads(raw.strip())


def faq_response(messages: list[dict]) -> dict:
    return _call_llm(messages, SYSTEM_PROMPT)


def generate_summary(
    messages: list[dict],
    qualification_data: dict,
    sop_gaps: list[str],
    escalated: bool,
    escalation_reason: Optional[str],
    duration: int,
) -> dict:
    transcript = "\n".join(
        f"{m['role'].upper()}: {m['content']}" for m in messages
    )
    user_content = SUMMARY_USER_TEMPLATE.format(
        transcript=transcript,
        qualification_data=json.dumps(qualification_data),
        sop_gaps=json.dumps(sop_gaps),
        escalated=str(escalated).lower(),
        escalation_reason=escalation_reason or "null",
        duration=duration,
    )
    return _call_llm(
        [{"role": "user", "content": user_content}],
        SUMMARY_SYSTEM,
    )


# ─── Escalation logging ───────────────────────────────────────────────────────

def log_escalation(reason: str, trigger_message: str, stage: str) -> None:
    entry = {
        "timestamp": datetime.now().isoformat(),
        "reason": reason,
        "trigger_message": trigger_message,
        "stage_at_escalation": stage,
    }
    log_path = os.path.join(os.path.dirname(__file__), "escalation_log.jsonl")
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")
    _print_system(f"ESCALATION LOGGED -> {reason}")


# ─── Display helpers ──────────────────────────────────────────────────────────

def _divider(char: str = "-", width: int = 62) -> None:
    print("\n" + char * width + "\n")


def _print_bloom(msg: str) -> None:
    print(f"  Bloom : {msg}")


def _print_system(msg: str) -> None:
    print(f"  [SYS] {msg}")


# ─── Main workflow ────────────────────────────────────────────────────────────

def run():
    # State
    stage = Stage.FAQ
    messages: list[dict] = []
    unanswered_streak = 0
    escalated = False
    escalation_reason: Optional[str] = None
    qualification_index = 0
    qualification_data: dict = {}
    sop_gaps: list[str] = []
    session_start = datetime.now()

    _divider("=")
    print("   Bloom Aesthetics Clinic -- AI Support (Closira Demo)")
    _divider("=")
    print("   Commands: 'done'     -> end session & view summary")
    print("             'escalate' -> request a human agent")
    _divider()

    opening = (
        "Hi there! I'm Bloom, the virtual assistant for Bloom Aesthetics Clinic. "
        "How can I help you today?"
    )
    _print_bloom(opening)
    messages.append({"role": "assistant", "content": opening})

    while True:
        print()
        try:
            user_input = input("  You   : ").strip()
        except (KeyboardInterrupt, EOFError):
            user_input = "done"

        if not user_input:
            continue

        # ── End session ───────────────────────────────────────────────────────
        if user_input.lower() in ("done", "bye", "goodbye", "exit", "quit"):
            stage = Stage.ENDED
            _divider()
            _print_system("Session ended. Generating summary...")
            duration = max(1, (datetime.now() - session_start).seconds // 60)
            try:
                summary = generate_summary(
                    messages, qualification_data, sop_gaps,
                    escalated, escalation_reason, duration
                )
            except Exception as e:
                _print_system(f"Summary generation failed: {e}")
                break

            _divider("=")
            print("  SESSION SUMMARY")
            _divider()
            print(json.dumps(summary, indent=4))
            _divider("=")

            summary_path = os.path.join(os.path.dirname(__file__), "session_summary.json")
            with open(summary_path, "w", encoding="utf-8") as f:
                json.dump(summary, f, indent=2)
            _print_system("Summary saved -> session_summary.json")
            break

        # ── Explicit escalation ───────────────────────────────────────────────
        if user_input.lower() in ("escalate", "human", "speak to human", "human agent", "agent"):
            reason = "Customer explicitly requested a human agent"
            log_escalation(reason, user_input, stage)
            escalated = True
            escalation_reason = reason
            stage = Stage.ESCALATED
            farewell = (
                "Of course — I completely understand. I've flagged your conversation "
                "and one of our team members will be in touch with you very shortly. "
                "Thank you for reaching out to Bloom Aesthetics Clinic!"
            )
            _print_bloom(farewell)
            messages.append({"role": "user", "content": user_input})
            messages.append({"role": "assistant", "content": farewell})
            _print_system("Conversation handed off. Exiting.")
            break

        messages.append({"role": "user", "content": user_input})

        # ── Stage: QUALIFICATION ──────────────────────────────────────────────
        if stage == Stage.QUALIFICATION:
            # Save previous answer (index already incremented after question was asked)
            answer_key_index = qualification_index - 1
            if 0 <= answer_key_index < len(QUALIFICATION_KEYS):
                qualification_data[QUALIFICATION_KEYS[answer_key_index]] = user_input

            # Check for escalation signals even during qualification
            try:
                check = faq_response(messages)
                if check.get("escalate"):
                    reason = check.get("escalation_reason") or "Escalation trigger during qualification"
                    log_escalation(reason, user_input, stage)
                    escalated = True
                    escalation_reason = reason
                    stage = Stage.ESCALATED
                    response_msg = check.get("message", "")
                    messages.append({"role": "assistant", "content": response_msg})
                    _print_bloom(response_msg)
                    _print_bloom(
                        "I've flagged this conversation for one of our specialists. "
                        "They'll follow up with you shortly!"
                    )
                    break
            except Exception:
                pass  # Don't block qualification on a failed check

            # Ask next question or finish qualification
            if qualification_index < len(QUALIFICATION_QUESTIONS):
                q = QUALIFICATION_QUESTIONS[qualification_index]
                qualification_index += 1
                messages.append({"role": "assistant", "content": q})
                _print_bloom(q)
            else:
                # Qualification complete
                stage = Stage.FAQ
                done_msg = (
                    "Thank you — that's really helpful! I've noted your preferences. "
                    "Is there anything else I can help you with today?"
                )
                messages.append({"role": "assistant", "content": done_msg})
                _print_bloom(done_msg)
                _print_system(f"Qualification complete -> {qualification_data}")
            continue

        # ── Stage: FAQ ────────────────────────────────────────────────────────
        try:
            result = faq_response(messages)
        except (json.JSONDecodeError, KeyError, IndexError, Exception) as exc:
            _print_system(f"Response error ({exc}). Using safe fallback.")
            fallback = (
                "I'm having a little trouble at the moment. Let me connect you with "
                "our team who will be happy to assist you directly."
            )
            messages.append({"role": "assistant", "content": fallback})
            _print_bloom(fallback)
            continue

        message = result.get("message", "")
        escalate = result.get("escalate", False)
        esc_reason = result.get("escalation_reason")
        confidence = result.get("confidence", "high")
        is_out_of_scope = result.get("is_out_of_scope", False)
        detected_intent = result.get("detected_intent", "")

        # Track SOP gaps
        if is_out_of_scope and user_input not in sop_gaps:
            sop_gaps.append(user_input)

        # Track unanswered streak for auto-escalation
        if is_out_of_scope or confidence == "low":
            unanswered_streak += 1
        else:
            unanswered_streak = 0

        if unanswered_streak >= 2 and not escalate:
            escalate = True
            esc_reason = "More than 2 consecutive questions could not be answered from SOP"

        # Handle escalation
        if escalate:
            log_escalation(esc_reason or "Unknown trigger", user_input, stage)
            escalated = True
            escalation_reason = esc_reason
            stage = Stage.ESCALATED
            messages.append({"role": "assistant", "content": message})
            _print_bloom(message)
            _print_bloom(
                "I've flagged this conversation so one of our team members can follow up "
                "with you directly. We'll be in touch very soon!"
            )
            break

        # Normal FAQ response
        messages.append({"role": "assistant", "content": message})
        _print_bloom(message)

        # Trigger qualification if booking/service interest detected and not yet qualified
        booking_intents = {
            "booking_request", "price_inquiry", "service_inquiry",
            "botox", "filler", "consultation", "appointment"
        }
        should_qualify = (
            stage == Stage.FAQ
            and qualification_index == 0
            and (
                detected_intent.lower() in booking_intents
                or any(kw in detected_intent.lower() for kw in booking_intents)
            )
            and len([m for m in messages if m["role"] == "user"]) >= 1
        )
        if should_qualify:
            qualify_prompt = (
                "\nTo make sure we give you the best possible guidance, "
                "may I ask a few quick questions?"
            )
            messages.append({"role": "assistant", "content": qualify_prompt})
            _print_bloom(qualify_prompt)

            # Ask first qualification question immediately
            first_q = QUALIFICATION_QUESTIONS[0]
            qualification_index = 1
            messages.append({"role": "assistant", "content": first_q})
            _print_bloom(first_q)
            stage = Stage.QUALIFICATION


if __name__ == "__main__":
    run()
