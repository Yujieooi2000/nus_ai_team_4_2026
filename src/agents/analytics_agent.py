from collections import defaultdict
from datetime import datetime
import statistics


class AnalyticsAgent:
    def __init__(self, analytics_database):
        """
        Enhanced Enterprise Analytics Agent
        Maintains backward compatibility while adding:
        - Drift detection
        - Hallucination tracking
        - Retrieval confidence metrics
        - Knowledge gap detection
        - Sentiment trend tracking
        """
        self.analytics_database = analytics_database

    # =================================================
    # EXISTING FUNCTION (Enhanced Internally)
    # =================================================
    def log_interaction(self, request, analysis, resolution, conversation_history):
        """
        Logs detailed interaction data.
        """

        log_entry = {
            # Existing fields
            'timestamp': datetime.utcnow().isoformat(),
            'request': request,
            'analysis': analysis,
            'resolution': resolution,
            'history': conversation_history,

            # NEW Enterprise Fields
            'category': analysis.get('category'),
            'priority': analysis.get('priority'),
            'sentiment': analysis.get('sentiment'),
            'triage_confidence': analysis.get('confidence_score'),

            'retrieval_confidence': resolution.get('retrieval_confidence'),
            'verification_passed': resolution.get('verification_passed'),
            'hallucination_detected': resolution.get('hallucination_detected', False),
            'escalated': resolution.get('escalated', False),
            'conversation_length': len(conversation_history)
        }

        if isinstance(self.analytics_database, list):
            self.analytics_database.append(log_entry)

    # =================================================
    # EXISTING FUNCTION (Enhanced Internally)
    # =================================================
    def generate_insights(self):
        """
        Generates business + AI performance insights.
        """

        if not isinstance(self.analytics_database, list) or not self.analytics_database:
            return {
                'total_requests': 0,
                'resolved_count': 0,
                'resolution_rate': 0.0,
                'category_breakdown': {}
            }

        total_requests = len(self.analytics_database)

        resolved_count = sum(
            1 for entry in self.analytics_database
            if entry.get('resolution', {}).get('status') == 'resolved'
        )

        resolution_rate = (resolved_count / total_requests) * 100

        # Category breakdown
        category_counts = defaultdict(int)
        for entry in self.analytics_database:
            category = entry.get('analysis', {}).get('category', 'unknown')
            category_counts[category] += 1

        # NEW Metrics
        hallucination_count = sum(
            1 for entry in self.analytics_database
            if entry.get('hallucination_detected')
        )

        escalation_count = sum(
            1 for entry in self.analytics_database
            if entry.get('escalated')
        )

        retrieval_scores = [
            entry.get('retrieval_confidence')
            for entry in self.analytics_database
            if entry.get('retrieval_confidence') is not None
        ]

        avg_retrieval_confidence = (
            statistics.mean(retrieval_scores)
            if retrieval_scores else 0
        )

        insights = {
            'total_requests': total_requests,
            'resolved_count': resolved_count,
            'resolution_rate': f"{resolution_rate:.2f}%",
            'category_breakdown': dict(category_counts),

            # NEW AI Metrics
            'hallucination_rate': round(hallucination_count / total_requests, 3),
            'escalation_rate': round(escalation_count / total_requests, 3),
            'avg_retrieval_confidence': round(avg_retrieval_confidence, 3)
        }

        return insights

    # =================================================
    # NEW FUNCTION: Drift Detection
    # =================================================
    def detect_drift(self, confidence_threshold=0.6, escalation_threshold=0.3):
        """
        Detects system performance degradation.
        """

        insights = self.generate_insights()

        drift_flags = []

        if insights.get('avg_retrieval_confidence', 1) < confidence_threshold:
            drift_flags.append("Retrieval confidence degraded")

        if insights.get('escalation_rate', 0) > escalation_threshold:
            drift_flags.append("Escalation rate increased")

        if insights.get('hallucination_rate', 0) > 0.15:
            drift_flags.append("Hallucination rate high")

        return {
            "drift_detected": len(drift_flags) > 0,
            "issues": drift_flags
        }

    # =================================================
    # NEW FUNCTION: Knowledge Gap Detection
    # =================================================
    def detect_knowledge_gaps(self, escalation_threshold=5):
        """
        Identifies categories frequently escalated.
        """

        category_escalations = defaultdict(int)

        for entry in self.analytics_database:
            if entry.get('escalated'):
                category = entry.get('analysis', {}).get('category', 'unknown')
                category_escalations[category] += 1

        gaps = {
            category: count
            for category, count in category_escalations.items()
            if count >= escalation_threshold
        }

        return gaps

    # =================================================
    # NEW FUNCTION: Sentiment Trend
    # =================================================
    def sentiment_trend(self):
        """
        Tracks customer sentiment distribution.
        """

        sentiment_counts = defaultdict(int)

        for entry in self.analytics_database:
            sentiment = entry.get('analysis', {}).get('sentiment', 'unknown')
            sentiment_counts[sentiment] += 1

        return dict(sentiment_counts)

    # =================================================
    # NEW FUNCTION: AI Risk Report
    # =================================================
    def generate_ai_risk_report(self):
        """
        Generates a Responsible AI compliance summary.
        """

        insights = self.generate_insights()
        drift = self.detect_drift()

        return {
            "system_health": insights,
            "drift_status": drift,
            "recommendation": (
                "Review prompt versions and retrain embeddings"
                if drift["drift_detected"]
                else "System operating within acceptable thresholds"
            )
        }

    # =================================================
    # NEW FUNCTION: Provide Feedback to Triage Agent
    # =================================================
    def feedback_to_triage(self):
        """
        Provides improvement signals to the Triage Agent.
        """

        negative_sentiment_cases = [
            entry for entry in self.analytics_database
            if entry.get('analysis', {}).get('sentiment') == 'negative'
            and not entry.get('escalated')
        ]

        misrouted_cases = [
            entry for entry in self.analytics_database
            if entry.get('escalated')
            and entry.get('analysis', {}).get('priority') == 'low'
        ]

        return {
            "adjust_priority_rules": len(misrouted_cases) > 5,
            "improve_sentiment_detection": len(negative_sentiment_cases) > 10,
            "suggestion": "Refine urgency keyword detection and sentiment thresholds."
        }

    # =================================================
    # NEW FUNCTION: Provide Feedback to IR Agent
    # =================================================
    def feedback_to_information_retrieval(self):
        """
        Provides improvement signals to the Retrieval Agent.
        """

        low_confidence_cases = [
            entry for entry in self.analytics_database
            if entry.get('retrieval_confidence', 1) < 0.4
        ]

        escalation_after_low_confidence = [
            entry for entry in low_confidence_cases
            if entry.get('escalated')
        ]

        return {
            "increase_top_k": len(low_confidence_cases) > 10,
            "improve_embeddings": len(escalation_after_low_confidence) > 5,
            "suggestion": "Enhance embedding quality or expand knowledge base coverage."
        }

    # =================================================
    # NEW FUNCTION: Provide Feedback to Verification Agent
    # =================================================
    def feedback_to_verification(self):
        """
        Provides improvement signals to Verification Agent.
        """

        hallucination_cases = [
            entry for entry in self.analytics_database
            if entry.get('hallucination_detected')
        ]

        failed_verification = [
            entry for entry in self.analytics_database
            if not entry.get('verification_passed', True)
        ]

        return {
            "tighten_grounding_rules": len(hallucination_cases) > 5,
            "increase_strictness": len(failed_verification) > 10,
            "suggestion": "Enforce stricter grounding validation and reduce creative generation."
        }

    # =================================================
    # NEW FUNCTION: Provide Feedback to Escalation Agent
    # =================================================
    def feedback_to_escalation(self):
        """
        Provides optimization signals to Escalation Agent.
        """

        unnecessary_escalations = [
            entry for entry in self.analytics_database
            if entry.get('escalated')
            and entry.get('verification_passed')
            and entry.get('retrieval_confidence', 0) > 0.7
        ]

        return {
            "reduce_escalation_threshold": len(unnecessary_escalations) > 5,
            "suggestion": "Refine escalation threshold to avoid overloading human agents."
        }

    # =================================================
    # NEW FUNCTION: Global Feedback Summary
    # =================================================
    def generate_system_feedback(self):
        """
        Generates structured feedback for all agents.
        """

        return {
            "triage_feedback": self.feedback_to_triage(),
            "retrieval_feedback": self.feedback_to_information_retrieval(),
            "verification_feedback": self.feedback_to_verification(),
            "escalation_feedback": self.feedback_to_escalation()
        }
