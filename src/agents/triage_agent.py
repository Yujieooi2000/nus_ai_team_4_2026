import re
from typing import Dict, Any
from dataclasses import dataclass
from textblob import TextBlob
import joblib
import os

@dataclass
class TriageResult:
    category: str
    priority: str
    sentiment: str
    confidence_score: float
    risk_score: float
    requires_human: bool
    explanation: str


class TriageAgent:

    def __init__(self):
        model_path = os.path.join(os.path.dirname(__file__), "..", "intent_model.joblib")
        model_path = os.path.abspath(model_path)

        if os.path.exists(model_path):
            self.intent_model = joblib.load(model_path)
        else:
            self.intent_model = None
        
        self.billing_keywords = ['bill', 'payment', 'invoice', 'charge', 'refund']
        self.tech_keywords = ['error', 'broken', 'bug', 'fail', 'crash', 'slow']
        self.account_keywords = ['password', 'account', 'login', 'access']
        self.urgent_keywords = ['urgent', 'immediate', 'emergency', 'asap', 'help']
        
        self.injection_patterns = [
            r"ignore\s+previous\s+instructions",
            r"forget\s+your\s+instructions",
            r"system\s+prompt",
            r"you\s+are\s+now",
            r"override",
            r"bypass",
            r"act\s+as"
        ]

    # -----------------------------
    # Security Layer
    # -----------------------------
    def validate_input(self, text: str) -> bool:
        text_lower = text.lower()
        for pattern in self.injection_patterns:
            if re.search(pattern, text_lower):
                return False
        return True

    def compute_risk_score(self, text: str) -> float:
        risk = 0.0
        for pattern in self.injection_patterns:
            if re.search(pattern, text.lower()):
                risk += 0.3
        if any(word in text.lower() for word in self.urgent_keywords):
            risk += 0.2
        return min(risk, 1.0)

    # -----------------------------
    # Sentiment Analysis
    # -----------------------------
    def analyze_sentiment(self, text: str) -> str:
        polarity = TextBlob(text).sentiment.polarity
        if polarity > 0.2:
            return "positive"
        elif polarity < -0.2:
            return "negative"
        else:
            return "neutral"

    # -----------------------------
    # Core Analysis
    # -----------------------------
    def analyze_request(self, request: Dict[str, Any]) -> TriageResult:

        text = request.get("body", "")
        predicted_intent = self.predict_intent(text)
        text_lower = text.lower()

        decision_trace = []

        # ---- Security Check ----
        if not self.validate_input(text):
            return TriageResult(
                category="security_alert",
                priority="high",
                sentiment="negative",
                confidence_score=0.99,
                risk_score=1.0,
                requires_human=True,
                explanation="Prompt injection pattern detected."
            )

        # ---- Category Detection ----
        category = predicted_intent if predicted_intent else "general_inquiry"
        confidence = 0.8 if predicted_intent else 0.5

        def keyword_match(keywords, label):
            for word in keywords:
                if word in text_lower:
                    return word
            return None

        if keyword := keyword_match(self.billing_keywords, "billing"):
            category = "billing"
            confidence = 0.85
            decision_trace.append(f"Matched billing keyword '{keyword}'")

        elif keyword := keyword_match(self.tech_keywords, "technical_support"):
            category = "technical_support"
            confidence = 0.85
            decision_trace.append(f"Matched technical keyword '{keyword}'")

        elif keyword := keyword_match(self.account_keywords, "account_issue"):
            category = "account_issue"
            confidence = 0.85
            decision_trace.append(f"Matched account keyword '{keyword}'")

        if "order status" in text_lower or "where is my order" in text_lower:
            category = "order_status"
            confidence = 0.9
            decision_trace.append("Matched order status phrase")

        # ---- Priority Detection ----
        priority = "low"
        if any(word in text_lower for word in self.urgent_keywords):
            priority = "high"
            decision_trace.append("Urgent keyword detected")

        # ---- Sentiment ----
        sentiment = self.analyze_sentiment(text)
        decision_trace.append(f"Sentiment detected as {sentiment}")

        # ---- Risk Score ----
        risk_score = self.compute_risk_score(text)

        # ---- Human Escalation Logic ----
        requires_human = False
        if priority == "high" or risk_score > 0.7 or sentiment == "negative":
            requires_human = True

        # Build a structured, human-readable explanation for the XAI trace
        xai_parts = []

        # How the category was determined
        if decision_trace and decision_trace[0].startswith("Matched"):
            xai_parts.append(f"Category: {category.replace('_', ' ').title()} ({decision_trace[0].lower()})")
        elif predicted_intent:
            xai_parts.append(f"Category: {category.replace('_', ' ').title()} (ML model prediction)")
        else:
            xai_parts.append(f"Category: {category.replace('_', ' ').title()} (no specific keyword matched)")

        xai_parts.append(f"Confidence: {confidence:.0%}")
        xai_parts.append(f"Sentiment: {sentiment.title()}")

        if priority == "high":
            xai_parts.append("Priority: High (urgent keyword detected)")
        else:
            xai_parts.append("Priority: Low")

        if requires_human:
            escalation_reasons = []
            if priority == "high":
                escalation_reasons.append("high priority")
            if sentiment == "negative":
                escalation_reasons.append("negative sentiment")
            if risk_score > 0.7:
                escalation_reasons.append(f"high risk score ({risk_score:.2f})")
            xai_parts.append(f"Routed to: Human Agent ({', '.join(escalation_reasons)})")
        else:
            xai_parts.append("Routed to: AI Resolution")

        explanation = " | ".join(xai_parts)

        return TriageResult(
            category=category,
            priority=priority,
            sentiment=sentiment,
            confidence_score=confidence,
            risk_score=risk_score,
            requires_human=requires_human,
            explanation=explanation
        )

    # -----------------------------
    # Routing Logic
    # -----------------------------
    def route_request(self, analysis: TriageResult) -> str:

        if analysis.category == "security_alert":
            return "EscalationAgent"

        if analysis.requires_human:
            return "EscalationAgent"

        if analysis.category in ["billing", "account_issue", "order_status"]:
            return "ResolutionAgent"

        if analysis.category in ["technical_support", "general_inquiry"]:
            return "InformationRetrievalAgent"

        return "EscalationAgent"
    
    #Model prediction method
    def predict_intent(self, text: str):
        if self.intent_model is None:
            return None
        return self.intent_model.predict([text])[0]
