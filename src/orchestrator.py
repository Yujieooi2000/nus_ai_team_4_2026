import json
import os
from agents.triage_agent import TriageAgent
from agents.information_retrieval_agent import InformationRetrievalAgent
from agents.resolution_agent import ResolutionAgent
from agents.reflection_agent import ReflectionAgent
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

        self.info_agent = InformationRetrievalAgent(
            knowledge_base=self.knowledge_base,
            use_vector_db=True
        )

        self.resolution_agent = ResolutionAgent()
        self.conversation_agent = ConversationAgent(api_key)
        self.verification_agent = VerificationAgent(api_key)
        self.reflection_agent = ReflectionAgent()
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
        state["triage_result"] = analysis.__dict__

        # =================================================
        # 3 ESCALATE DIRECTLY IF TRIAGE REQUIRES
        # =================================================
        if route == "EscalationAgent":

            escalation = self.escalation_agent.process(state)

            response = {
                "status": "escalated",
                "queue": escalation["queue"],
                "message": "Your case has been escalated. Our support team will review it and follow up with you shortly."
            }

            final_history = history.copy()
            final_history.append({"role": "user", "content": user_input})
            final_history.append({"role": "assistant", "content": response["message"]})
            state["history"] = final_history

            self.analytics_agent.log_interaction(
                request,
                analysis.__dict__,
                response,
                state["history"]
            )

            return {
                "agent": "EscalationAgent",
                "analysis": analysis.__dict__,
                "security": state["security_result"],
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
        state["knowledge"] = retrieval_response.get("answer", "")

        # =================================================
        # 5 RESOLUTION
        # =================================================
        resolution = self.resolution_agent.process(state)
        state["resolution_result"] = resolution

        # =================================================
        # 6 CONVERSATION (DRAFT REPLY)
        # =================================================
        conversation = self.conversation_agent.process(state)
        draft_reply = conversation["reply"]

        state["reply"] = draft_reply
        state["draft_reply"] = draft_reply

        # =================================================
        # 7 VERIFICATION ON DRAFT
        # =================================================
        verification = self.verification_agent.verify(
            user_query=user_input,
            retrieved_docs=state["retrieved_docs"],
            generated_answer=draft_reply
        )
        state["verification_result"] = verification

        state["verification_status"] = "passed" if verification.is_factual else "failed"
        state["intent_confidence"] = state["triage_result"].get("confidence_score", 1.0)
        state["issue_type"] = state["triage_result"].get("category", "general")
        # =================================================
        # 8 REFLECTION ON DRAFT
        # =================================================
        reflection = self.reflection_agent.process(state)
        state["reflection_result"] = reflection

        # =================================================
        # 9 DECIDE ACCEPT / REVISE / ESCALATE
        # =================================================
        escalate = False
        revise = False

        category = state["triage_result"].get("category", "general_inquiry")
        risk_level = state.get("security_result", {}).get("risk_level", "low")

        low_risk_categories = {
            "account_issue",
            "billing",
            "plan_change",
            "general_inquiry",
            "technical_support",
            "roaming",
            "sim_issue"
        }

        is_low_risk = (
            category in low_risk_categories and
            risk_level not in ["high", "critical"]
        )

        # For low-risk issues, verification/reflection should trigger revision first,
        # not immediate escalation.
        if verification.recommendation == "ESCALATE":
            if is_low_risk:
                revise = True
            else:
                escalate = True
        elif verification.recommendation == "REVISE":
            revise = True

        if reflection["reflection_action"] == "ESCALATE_OR_RETRY":
            if is_low_risk:
                revise = True
            else:
                escalate = True
        elif reflection["reflection_action"] == "REVISE_REPLY":
            revise = True

        if resolution.get("needs_escalation", False):
            escalate = True

        final_reply = draft_reply
        final_verification = verification
        final_reflection = reflection

        # =================================================
        # 10 REVISE IF NEEDED
        # =================================================
        if not escalate and revise:
            revised_reply = self.conversation_agent.revise_reply(state)
            state["reply"] = revised_reply
            state["revised_reply"] = revised_reply

            re_verification = self.verification_agent.verify(
                user_query=user_input,
                retrieved_docs=state["retrieved_docs"],
                generated_answer=revised_reply
            )
            state["verification_result"] = re_verification
            state["verification_status"] = "passed" if re_verification.is_factual else "failed"
            re_reflection = self.reflection_agent.process(state)
            state["reflection_result"] = re_reflection

            final_reply = revised_reply
            final_verification = re_verification
            final_reflection = re_reflection

            if re_verification.recommendation == "ESCALATE":
                if is_low_risk:
                    escalate = False
                else:
                    escalate = True

            if re_reflection["reflection_action"] == "ESCALATE_OR_RETRY":
                if is_low_risk:
                    escalate = False
                else:
                    escalate = True

        # =================================================
        # 11 FINAL RESPONSE
        # =================================================
        if escalate:
            escalation = self.escalation_agent.process(state)

            response = {
                "status": "escalated",
                "queue": escalation["queue"],
                "message": "Your case has been escalated. Our support team will review it and follow up with you shortly."
            }
        else:
            response = {
                "status": "resolved",
                "message": final_reply,
                "confidence": final_verification.confidence_score
            }

        # =================================================
        # 12 FINALIZE HISTORY
        # =================================================
        final_history = history.copy()
        final_history.append({"role": "user", "content": user_input})
        final_history.append({"role": "assistant", "content": response["message"]})
        state["history"] = final_history

        # =================================================
        # 13 ANALYTICS LOGGING
        # =================================================
        self.analytics_agent.log_interaction(
            request,
            analysis.__dict__,
            response,
            state["history"]
        )

        final_agent = "EscalationAgent" if response["status"] == "escalated" else route

        return {
            "agent": final_agent,
            "analysis": analysis.__dict__,
            "security": state["security_result"],
            "resolution": resolution,
            "verification": {
                "recommendation": final_verification.recommendation,
                "confidence_score": final_verification.confidence_score,
                "reasoning": final_verification.reasoning,
                "unsupported_claims": final_verification.unsupported_claims,
                "is_factual": final_verification.is_factual,
                "hallucination_detected": final_verification.hallucination_detected
            },
            "reflection": final_reflection,
            "response": response
        }

    # --------------------------------------------------
    # HITL: Generate Suggested Response for Escalated Tickets
    # --------------------------------------------------

    def generate_suggested_response(self, conversation_history: list) -> str:
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
                    "Keep it concise (2-4 sentences). Write only the customer-facing reply."
                )
            }
        ]

        messages.extend(conversation_history)

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