from typing import Dict, List

class ReflectionAgent:

    def __init__(self):
        self.bad_reply_keywords = [
            "i do not know",
            "i'm not sure",
            "cannot help",
            "unable to help",
            "no idea",
            "maybe",
            "probably",
            "perhaps"
        ]

        self.telco_required_action_keywords = [
            "verify",
            "verification",
            "identity",
            "support",
            "agent",
            "billing",
            "sim",
            "network",
            "account"
        ]

    def detect_low_quality_reply(self, reply: str) -> bool:
        lowered = reply.lower()
        return any(keyword in lowered for keyword in self.bad_reply_keywords)

    def detect_too_short_reply(self, reply: str) -> bool:
        return len(reply.strip()) < 20

    def detect_missing_action_guidance(self, user_input: str, reply: str) -> bool:
        """
        Simple rule:
        if user asks about an operational telco issue,
        but reply contains no useful action-related wording,
        mark as weak/incomplete.
        """
        telco_issue_words = [
            "sim", "otp", "billing", "bill", "internet", "network",
            "signal", "roaming", "esim", "port out", "data", "wifi"
        ]

        user_lower = user_input.lower()
        reply_lower = reply.lower()

        user_has_telco_issue = any(word in user_lower for word in telco_issue_words)
        reply_has_action = any(word in reply_lower for word in self.telco_required_action_keywords)

        return user_has_telco_issue and not reply_has_action

    def calculate_score(self, state: Dict) -> Dict:
        user_input = state.get("input", "")
        reply = state.get("reply", "")
        escalation_result = state.get("escalation_result", {})
        security_result = state.get("security_result", {})

        score = 0
        reasons = []

        if self.detect_low_quality_reply(reply):
            score += 2
            reasons.append("Reply contains weak or uncertain language")

        if self.detect_too_short_reply(reply):
            score += 2
            reasons.append("Reply is too short")

        if self.detect_missing_action_guidance(user_input, reply):
            score += 2
            reasons.append("Reply may be missing clear next-step guidance")

        if security_result.get("risk_level") in ["high", "critical"]:
            score += 3
            reasons.append("High security risk detected")

        if escalation_result.get("escalate"):
            score += 3
            reasons.append("Escalation already recommended by escalation agent")

        return {
            "score": score,
            "reasons": reasons
        }

    def process(self, state: Dict) -> Dict:
        result = self.calculate_score(state)
        score = result["score"]

        # Suggested action rules
        if score >= 5:
            action = "ESCALATE_OR_RETRY"
        elif score >= 2:
            action = "REVISE_REPLY"
        else:
            action = "ACCEPT_REPLY"

        return {
            "reflection_score": score,
            "reflection_reasons": result["reasons"],
            "reflection_action": action
        }
