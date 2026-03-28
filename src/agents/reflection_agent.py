from typing import Dict

ESCALATE_SCORE_THRESHOLD = 5
REVISE_SCORE_THRESHOLD = 2


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
            "account",
            "restart",
            "check",
            "settings",
            "plan",
            "roaming"
        ]

    def detect_low_quality_reply(self, reply: str) -> bool:
        lowered = reply.lower()
        return any(keyword in lowered for keyword in self.bad_reply_keywords)

    def detect_too_short_reply(self, reply: str) -> bool:
        return len(reply.strip()) < 20

    def detect_missing_action_guidance(self, user_input: str, reply: str) -> bool:
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
        verification_result = state.get("verification_result", None)

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

        if verification_result is not None:
            recommendation = getattr(verification_result, "recommendation", None)
            hallucination_detected = getattr(verification_result, "hallucination_detected", False)
            is_factual = getattr(verification_result, "is_factual", True)

            if hallucination_detected:
                score += 1
                reasons.append("Verification agent detected possible unsupported content")

            if is_factual is False:
                score += 1
                reasons.append("Verification agent found possible factual inconsistency")

            if recommendation == "REVISE":
                score += 1
                reasons.append("Verification agent recommended revision")

            if recommendation == "ESCALATE":
                score += 1
                reasons.append("Verification agent recommended escalation")

        return {
            "score": score,
            "reasons": reasons
        }

    def process(self, state: Dict) -> Dict:
        result = self.calculate_score(state)
        score = result["score"]

        if score >= ESCALATE_SCORE_THRESHOLD:
            action = "ESCALATE_OR_RETRY"
        elif score >= REVISE_SCORE_THRESHOLD:
            action = "REVISE_REPLY"
        else:
            action = "ACCEPT_REPLY"

        return {
            "reflection_score": score,
            "reflection_reasons": result["reasons"],
            "reflection_action": action
        }