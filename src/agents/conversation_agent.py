from typing import Dict, List
from openai import OpenAI


class ConversationAgent:
    def __init__(self, api_key: str, model: str = "gpt-4o-mini"):
        self.client = OpenAI(api_key=api_key)
        self.model = model

    def call_llm(self, messages: List[Dict[str, str]]) -> str:
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=0.3
        )
        return response.choices[0].message.content.strip()

    def _is_gratitude_or_closing(self, text: str) -> bool:
        text = text.strip().lower()

        exact_phrases = {
            "thanks",
            "thank you",
            "thankyou",
            "ok thanks",
            "okay thanks",
            "thanks okay",
            "thx",
            "tq",
            "got it",
            "that helps",
            "help thanks",
            "is help thank you",
            "bye",
            "okay bye",
            "ok bye",
            "goodbye"
        }

        if text in exact_phrases:
            return True

        gratitude_keywords = ["thanks", "thank you", "thx", "tq", "appreciate it"]
        if any(keyword in text for keyword in gratitude_keywords) and len(text.split()) <= 6:
            return True

        return False

    def _gratitude_reply(self, text: str) -> str:
        text = text.strip().lower()

        bye_keywords = ["bye", "goodbye"]
        if any(word in text for word in bye_keywords):
            return "You're welcome. Have a nice day."

        return "You're welcome. Let me know if you need anything else."

    def _build_messages(self, state: Dict) -> List[Dict[str, str]]:
        user_input = state.get("input", "")
        history = state.get("history", [])
        knowledge = state.get("knowledge", "")
        resolution_result = state.get("resolution_result", {})

        resolution_summary = resolution_result.get("resolution_summary", "")
        resolution_steps = resolution_result.get("resolution_steps", [])
        needs_escalation = resolution_result.get("needs_escalation", False)

        steps_text = "\n".join(
            [f"{idx + 1}. {step}" for idx, step in enumerate(resolution_steps)]
        )

        escalation_note = (
            "This case may require escalation or human support."
            if needs_escalation else
            "Provide a helpful actionable answer the user can try first."
        )

        system_prompt = (
            "You are a helpful and empathetic Telco Customer Support assistant. "
            "Your job is to generate a draft reply to the user. "
            "Use the provided resolution summary, resolution steps, and retrieved knowledge. "
            "Write in a natural, friendly, chatbot-style tone. "
            "Be clear, simple, and helpful. "
            "Do not sound like a formal email or letter. "
            "Do not include subject lines, greetings, sign-offs, or placeholder names. "
            "Do not mention internal agents, system design, orchestration, reflection, or verification. "
            "If the case may require escalation, say so in a simple and natural way. "
            "Keep the answer concise but actionable. "
            "You must follow this exact format: "
            "Line 1: one short empathy or acknowledgement sentence. "
            "Line 2: 'Please try these steps:' if there are steps. "
            "Next lines: numbered steps, one step per line. "
            "Final line: one short closing sentence. "
            "Use line breaks exactly as requested. "
            "Do not return everything in one paragraph."
        )

        user_prompt = f"""
Customer issue:
{user_input}

Retrieved knowledge:
{knowledge}

Resolution summary:
{resolution_summary}

Resolution steps:
{steps_text}

Instruction:
{escalation_note}

Write the draft reply to the user.

Output rules:
- Use plain text only.
- Start with one short sentence.
- Then put the troubleshooting steps on separate numbered lines.
- Add one short final sentence on a new line.
- Do not combine everything into one paragraph.
"""

        messages = [{"role": "system", "content": system_prompt}]

        if history:
            messages.extend(history)

        messages.append({"role": "user", "content": user_prompt})
        return messages

    def process(self, state: Dict) -> Dict:
        user_input = state.get("input", "")

        if self._is_gratitude_or_closing(user_input):
            return {
                "reply": self._gratitude_reply(user_input)
            }

        messages = self._build_messages(state)
        reply = self.call_llm(messages)

        return {
            "reply": reply
        }

    def revise_reply(self, state: Dict) -> str:
        user_input = state.get("input", "")

        if self._is_gratitude_or_closing(user_input):
            return self._gratitude_reply(user_input)

        knowledge = state.get("knowledge", "")
        resolution_result = state.get("resolution_result", {})
        draft_reply = state.get("reply", "")
        verification_result = state.get("verification_result", None)
        reflection_result = state.get("reflection_result", {})

        resolution_summary = resolution_result.get("resolution_summary", "")
        resolution_steps = resolution_result.get("resolution_steps", [])

        steps_text = "\n".join(
            [f"{idx + 1}. {step}" for idx, step in enumerate(resolution_steps)]
        )

        verification_notes = ""
        if verification_result is not None:
            unsupported_claims = getattr(verification_result, "unsupported_claims", [])
            reasoning = getattr(verification_result, "reasoning", "")
            recommendation = getattr(verification_result, "recommendation", "")
            verification_notes = f"""
Verification result:
- Recommendation: {recommendation}
- Reasoning: {reasoning}
- Unsupported claims: {unsupported_claims}
"""

        reflection_notes = f"""
Reflection result:
- Action: {reflection_result.get("reflection_action", "")}
- Reasons: {reflection_result.get("reflection_reasons", [])}
"""

        system_prompt = (
            "You are a helpful and empathetic Telco Customer Support assistant. "
            "Revise the draft reply so it is factual, supported by the retrieved knowledge, "
            "clear, concise, and actionable. "
            "Write in a natural, friendly, chatbot-style tone. "
            "Do not sound like a formal email or letter. "
            "Do not include subject lines, greetings, sign-offs, or placeholder names. "
            "Remove unsupported claims. "
            "Do not mention internal agents, verification, reflection, orchestration, or system logic. "
            "You must follow this exact format: "
            "Line 1: one short empathy or acknowledgement sentence. "
            "Line 2: 'Please try these steps:' if there are steps. "
            "Next lines: numbered steps, one step per line. "
            "Final line: one short closing sentence. "
            "Use line breaks exactly as requested. "
            "Do not return everything in one paragraph."
        )

        user_prompt = f"""
Customer issue:
{user_input}

Retrieved knowledge:
{knowledge}

Resolution summary:
{resolution_summary}

Resolution steps:
{steps_text}

Original draft reply:
{draft_reply}

{verification_notes}

{reflection_notes}

Instruction:
Rewrite the reply so it is safer, more accurate, more natural, and more actionable.

Output rules:
- Use plain text only.
- Start with one short sentence.
- Then put the troubleshooting steps on separate numbered lines.
- Add one short final sentence on a new line.
- Do not combine everything into one paragraph.

Return only the revised user-facing reply.
"""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]

        return self.call_llm(messages)