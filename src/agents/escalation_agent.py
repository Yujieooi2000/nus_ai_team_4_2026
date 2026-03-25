import re
from typing import Dict, List

ESCALATION_THRESHOLD = 5


class EscalationAgent:

    def __init__(self):
        self.human_request_keywords = [
            "human",
            "agent",
            "live agent",
            "customer service",
            "representative",
            "talk to someone",
            "talk to human",
            "real person",
            "support agent",
            "connect me to agent",
            "connect me to a human",
            "let me talk to a human",
            "let me talk to an agent",
            "transfer me",
            "speak to support",
            "chat with agent",
            "i want human support"
        ]

        self.frustration_keywords = [
            "not helpful",
            "useless",
            "frustrated",
            "angry",
            "bad service",
            "this is the third time",
            "still not working",
            "i already told you",
            "why still",
            "cannot work"
            "cannot solve",
            "waste of time",
            "so annoying",
            "very disappointed",
            "disappointed",
            "terrible service",
            "worst service",
            "this is ridiculous",
            "this is unacceptable",
            "not solved",
            "problem not solved",
            "issue not solved",
            "you are not helping",
            "you dont understand",
            "you do not understand",
            "are you even listening",
            "i said already",
            "how many times do i need to repeat",
            "i have repeated many times",
            "keep repeating",
            "same problem again",
            "again and again",
            "nobody helps",
            "no one helps",
            "no solution",
            "this is useless",
            "so useless",
            "completely useless",
            "very bad",
            "very poor service",
            "poor service",
            "horrible service",
            "this sucks",
            "i am upset",
            "i'm upset",
            "i am fed up",
            "i'm fed up",
            "fed up",
            "super annoyed",
            "really annoyed",
            "so frustrated",
            "extremely frustrated",
            "i am tired of this",
            "i'm tired of this",
            "tired of this",
            "this is wasting my time",
            "you keep asking the same thing",
            "this chatbot cannot help",
            "bot cannot help",
            "chatbot is useless",
            "i want to complain",
            "want to complain",
            "make a complaint",
            "i will complain",
            "i need a manager",
            "let me talk to your manager",
            "stop giving me the same answer",
            "this answer is not useful",
            "you are giving wrong information",
            "wrong information",
            "this is taking too long",
            "too slow",
            "so slow",
            "slow response",
            "nobody replied",
            "no reply yet",
            "i have been waiting",
            "i waited so long",
            "i've waited so long",
            "stupid"
        ]

        self.frustration_words = [
            "angry",
            "frustrated",
            "upset",
            "annoyed",
            "disappointed",
            "useless",
            "ridiculous",
            "unacceptable",
            "terrible",
            "horrible",
            "worst"
        ]

        self.telco_frustration_keywords = [
            "internet still down",
            "no signal again",
            "still no network",
            "data still not working",
            "wifi still not working",
            "broadband still down",
            "line still cut",
            "roaming still cannot use",
            "sim still not working",
            "otp not received again",
            "bill is still wrong",
            "charge is still wrong",
            "network still down",
            "still no internet",
            "my line is still down",
            "still cannot call",
            "still cannot receive sms",
            "still no service",
            "my data is not working",
            "internet is very slow again"
        ]

    def normalize_text(self, text: str) -> str:
        return re.sub(r"\s+", " ", text.strip().lower())

    def detect_human_request(self, text: str) -> bool:
        lowered = self.normalize_text(text)
        return any(keyword in lowered for keyword in self.human_request_keywords)

    def detect_frustration(self, text: str) -> bool:
        lowered = self.normalize_text(text)

        phrase_match = any(keyword in lowered for keyword in self.frustration_keywords)
        word_match = any(word in lowered for word in self.frustration_words)
        telco_match = any(keyword in lowered for keyword in self.telco_frustration_keywords)

        return phrase_match or word_match or telco_match

    def route_queue(self, state: Dict) -> str:
        security_result = state.get("security_result", {})
        issue_type = state.get("issue_type", "general")

        if security_result.get("jailbreak_detected"):
            return "security_compliance_team"

        if security_result.get("telco_sensitive_detected"):
            return "security_verification_team"

        routing_map = {
            "billing": "billing_support",
            "billing_dispute": "billing_support",
            "broadband": "technical_support",
            "mobile_data": "technical_support",
            "network": "technical_support",
            "sim_activation": "technical_support",
            "roaming": "technical_support",
            "fraud": "security_team",
            "sim_lost": "security_team",
            "identity_issue": "security_team",
            "termination": "retention_team",
            "cancellation": "retention_team",
            "plan_upgrade": "sales_team",
            "device_bundle": "sales_team"
        }

        return routing_map.get(issue_type, "general_support")

    def calculate_score(self, state: Dict) -> Dict:
        user_input = state.get("input", "")
        intent_confidence = state.get("intent_confidence", 1.0)
        failed_attempts = state.get("failed_attempts", 0)
        verification_status = state.get("verification_status", "not_verified")
        customer_type = state.get("customer_type", "normal")
        security_result = state.get("security_result", {})

        score = 0
        reasons = []
        if self.detect_human_request(user_input):
            score += 5
            reasons.append("Customer explicitly requested a human agent")

        if self.detect_frustration(user_input):
            score += 2
            reasons.append("Customer frustration detected")

        if failed_attempts >= 2:
            score += 3
            reasons.append(f"Failed attempts = {failed_attempts}")

        if intent_confidence < 0.60:
            score += 2
            reasons.append(f"Low intent confidence = {intent_confidence}")

        if customer_type in ["vip", "enterprise"]:
            score += 2
            reasons.append(f"Priority customer type = {customer_type}")

        if verification_status == "failed":
            score += 3
            reasons.append("Verification failed")

        if security_result.get("pii_found"):
            score += 1
            reasons.append("PII detected in customer message")

        if security_result.get("telco_sensitive_detected"):
            score += 4
            reasons.append("Sensitive telco operation detected")

        if security_result.get("jailbreak_detected"):
            score += 10
            reasons.append("Prompt injection / jailbreak detected")

        risk_level = security_result.get("risk_level", "low")

        if risk_level == "medium":
            score += 1
            reasons.append("Medium security risk level")
        elif risk_level == "high":
            score += 4
            reasons.append("High security risk level")
        elif risk_level == "critical":
            score += 10
            reasons.append("Critical security risk level")

        return {
            "score": score,
            "reasons": reasons
        }

    def build_handoff_summary(self, state: Dict, decision: Dict) -> Dict:
        security_result = state.get("security_result", {})
        history = state.get("history", [])

        return {
            "user_input": state.get("input", ""),
            "cleaned_input": security_result.get("cleaned_input", state.get("input", "")),
            "issue_type": state.get("issue_type", "general"),
            "intent_confidence": state.get("intent_confidence", 1.0),
            "failed_attempts": state.get("failed_attempts", 0),
            "verification_status": state.get("verification_status", "not_verified"),
            "customer_type": state.get("customer_type", "normal"),
            "risk_level": security_result.get("risk_level", "low"),
            "pii_found": security_result.get("pii_found", False),
            "telco_sensitive_detected": security_result.get("telco_sensitive_detected", False),
            "jailbreak_detected": security_result.get("jailbreak_detected", False),
            "recommended_queue": self.route_queue(state),
            "escalation_score": decision["score"],
            "escalation_reasons": decision["reasons"],
            "history": history
        }

    def process(self, state: Dict) -> Dict:
        decision = self.calculate_score(state)
        escalate = decision["score"] >= ESCALATION_THRESHOLD

        if escalate:
            return {
                "escalate": True,
                "queue": self.route_queue(state),
                "score": decision["score"],
                "reasons": decision["reasons"],
                "handoff_summary": self.build_handoff_summary(state, decision)
            }

        return {
            "escalate": False,
            "queue": None,
            "score": decision["score"],
            "reasons": decision["reasons"],
            "handoff_summary": None
        }
