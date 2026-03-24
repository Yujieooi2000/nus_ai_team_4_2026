import json
import os
from agents.triage_agent import TriageAgent
from agents.information_retrieval_agent import InformationRetrievalAgent
from agents.resolution_agent import ResolutionAgent
from agents.escalation_agent import EscalationAgent
from agents.analytics_agent import AnalyticsAgent
from agents.security_compliance_agent import SecurityComplianceAgent
from agents.verification_agent import VerificationAgent
from agents.conversation_agent import ConversationAgent


class Orchestrator:

    def __init__(self, api_key):

        # ----------------------------
        # Resources
        # ----------------------------

        _kb_path = os.path.join(os.path.dirname(__file__), "knowledge_base.json")
        with open(_kb_path, "r", encoding="utf-8") as f:
            self.knowledge_base = json.load(f)

        self.analytics_db = []

        # ----------------------------
        # Agents
        # ----------------------------

        self.security_agent = SecurityComplianceAgent()
        self.triage_agent = TriageAgent()
        
        # Use vector database for retrieval if available
        self.info_agent = InformationRetrievalAgent(
            knowledge_base=self.knowledge_base,
            use_vector_db=True  # Enable vector database search
        )
        
        self.conversation_agent = ConversationAgent(api_key)
        self.verification_agent = VerificationAgent(api_key)
        self.resolution_agent = ResolutionAgent()
        self.escalation_agent = EscalationAgent()
        self.analytics_agent = AnalyticsAgent(self.analytics_db)

    # --------------------------------------------------
    # Main Pipeline
    # --------------------------------------------------

    def process_request(self, user_input, history=None):

        if history is None:
            history = []

        request = {"body": user_input}

        state = {
            "input": user_input,
            "history": history
        }

        # =================================================
        # 1 SECURITY CHECK
        # =================================================

        security_result = self.security_agent.process(user_input)
        state["security_result"] = security_result

        if security_result["jailbreak_detected"]:
            return {
                "agent": "SecurityComplianceAgent",
                "response": {
                    "status": "blocked",
                    "message": "Request blocked due to security policy."
                }
            }

        # =================================================
        # 2 TRIAGE
        # =================================================

        analysis = self.triage_agent.analyze_request(request)
        route = self.triage_agent.route_request(analysis)

        # =================================================
        # 3 ESCALATE DIRECTLY IF TRIAGE REQUIRES
        # =================================================

        if route == "EscalationAgent":

            escalation = self.escalation_agent.process(state)

            response = {
                "status": "escalated",
                "queue": escalation["queue"],
                "message": "Connecting you to a human agent."
            }

            self.analytics_agent.log_interaction(
                request,
                analysis.__dict__,
                response,
                history
            )

            return {
                "agent": "EscalationAgent",
                "analysis": analysis.__dict__,
                "response": response
            }

        # =================================================
        # 4 KNOWLEDGE RETRIEVAL
        # =================================================

        retrieval = self.info_agent.search_knowledge_base(user_input)

        retrieval_response = self.info_agent.generate_response(
            user_input,
            retrieval
        )

        state["retrieved_docs"] = retrieval_response.get("retrieved_docs", [])
        state["knowledge"] = retrieval_response.get("answer")

        # =================================================
        # 5 LLM CONVERSATION
        # =================================================

        conversation = self.conversation_agent.process(state)

        reply = conversation["reply"]
        state["reply"] = reply
        state["history"] = conversation["history"]

        # =================================================
        # 6 VERIFICATION (FACT CHECK)
        # =================================================

        verification = self.verification_agent.verify(
            user_query=user_input,
            retrieved_docs=state["retrieved_docs"],
            generated_answer=reply
        )

        state["verification_result"] = verification

        # =================================================
        # 7 RESPONSE QUALITY CHECK
        # =================================================

        resolution = self.resolution_agent.process(state)

        state["resolution_result"] = resolution

        # =================================================
        # 8 ESCALATION DECISION
        # =================================================

        escalate = False

        if verification.recommendation == "ESCALATE":
            escalate = True

        if resolution["reflection_action"] == "ESCALATE_OR_RETRY":
            escalate = True

        if escalate:

            escalation = self.escalation_agent.process(state)

            response = {
                "status": "escalated",
                "queue": escalation["queue"],
                "message": "Your issue is being transferred to a support specialist."
            }

        else:

            response = {
                "status": "resolved",
                "message": reply,
                "confidence": verification.confidence_score
            }

        # =================================================
        # 9 ANALYTICS LOGGING
        # =================================================

        self.analytics_agent.log_interaction(
            request,
            analysis.__dict__,
            response,
            state["history"]
        )

        return {
            "agent": route,
            "analysis": analysis.__dict__,
            "response": response
        }

    # --------------------------------------------------
    # HITL: Generate Suggested Response for Escalated Tickets
    # --------------------------------------------------

    def generate_suggested_response(self, conversation_history: list) -> str:
        """
        Given a conversation history, asks the LLM to draft a suggested reply
        that a human support agent can review, approve, or modify.

        Returns the draft string, or None if generation fails.
        """
        if not conversation_history:
            return None

        messages = [
            {
                "role": "system",
                "content": (
                    "You are a professional Telco Customer Support specialist. "
                    "A customer conversation has been escalated for human agent review. "
                    "Based on the conversation history below, draft a clear, empathetic, "
                    "and actionable response that the human agent can send to the customer. "
                    "Keep it concise (2-4 sentences). Write only the customer-facing reply — "
                    "no internal notes, no prefixes like 'Draft:' or 'Suggested reply:'."
                )
            }
        ]

        # Include the full conversation history so the LLM has full context
        messages.extend(conversation_history)

        # Final instruction to trigger the draft
        messages.append({
            "role": "user",
            "content": (
                "[INTERNAL — do not include in reply] "
                "Please write a suggested response for the human agent to review."
            )
        })

        try:
            return self.conversation_agent.call_llm(messages)
        except Exception:
            return None

    # --------------------------------------------------
    # SYSTEM INSIGHTS
    # --------------------------------------------------

    def get_system_insights(self):

        return self.analytics_agent.generate_insights()