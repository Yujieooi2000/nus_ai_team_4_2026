from typing import Dict, List

class ResolutionAgent:

    def __init__(self):
        self.intent_steps = {
            "billing": [
                "Check the latest bill amount and billing date.",
                "Review whether there are any recent extra charges, add-ons, or overdue payments.",
                "Confirm whether auto-payment or a failed transaction may have caused the issue.",
                "If the charge is still unclear, contact billing support for detailed review."
            ],
            "technical_support": [
                "Restart the app or device first.",
                "Check whether the app is updated to the latest version.",
                "Try clearing cache or logging out and back in again.",
                "If the issue continues, contact technical support for further troubleshooting."
            ],
            "account_issue": [
                "Check whether the login details entered are correct.",
                "Try resetting the password if login is failing.",
                "Check whether identity verification or multi-factor authentication is causing the issue.",
                "If access is still blocked, contact account support for manual assistance."
            ],
            "sim_issue": [
                "Reinsert the SIM card properly into the device.",
                "Restart the phone after reinserting the SIM.",
                "Check whether the SIM is damaged, inactive, or not provisioned.",
                "If the SIM still does not work, contact support or visit a service center."
            ],
            "roaming": [
                "Check whether roaming is enabled on the mobile plan.",
                "Ensure mobile data and data roaming are switched on in phone settings.",
                "Restart the device after arriving at the destination country.",
                "If roaming still does not work, contact roaming support for assistance."
            ],
            "plan_change": [
                "Review the user's current mobile plan and requested new plan.",
                "Check whether the requested plan is eligible for change.",
                "Explain when the plan change will take effect.",
                "Advise the user to confirm the change through the app or customer support."
            ],
            "cancellation": [
                "Confirm which service or line the user wants to cancel.",
                "Check whether any contract period, early termination, or penalty applies.",
                "Explain the cancellation process clearly.",
                "If manual confirmation is required, direct the user to customer support."
            ],
            "complaint": [
                "Acknowledge the user's frustration and issue.",
                "Summarize the problem clearly so it can be handled properly.",
                "Advise the user that the complaint may be escalated for further review.",
                "Provide the next step for follow-up with support."
            ],
            "general": [
                "Understand the user's issue clearly.",
                "Provide the most relevant guidance based on the request.",
                "Offer the next step if the issue is not resolved.",
                "Escalate to support if manual intervention is needed."
            ]
        }

        self.intent_summary = {
            "billing": "The user needs help understanding or resolving a billing-related issue.",
            "technical_support": "The user is facing a technical problem and needs troubleshooting guidance.",
            "account_issue": "The user is having account access, login, or verification issues.",
            "sim_issue": "The user may be facing a SIM-related problem.",
            "roaming": "The user needs help with roaming setup or troubleshooting.",
            "plan_change": "The user wants guidance on changing a mobile plan.",
            "cancellation": "The user wants to understand or proceed with cancellation.",
            "complaint": "The user has raised a complaint and needs proper handling and follow-up.",
            "general": "The user needs general customer support guidance."
        }

        self.escalation_keywords = [
            "fraud",
            "legal",
            "supervisor",
            "manager",
            "urgent",
            "escalate",
            "cancel immediately"
        ]

    def detect_intent(self, state: Dict) -> str:
        triage_result = state.get("triage_result", {})
        intent = triage_result.get("category", "general")
        return intent or "general"

    def should_escalate(self, user_input: str, state: Dict) -> bool:
        lowered = user_input.lower()

        if any(keyword in lowered for keyword in self.escalation_keywords):
            return True

        security_result = state.get("security_result", {})
        if security_result.get("risk_level") in ["high", "critical"]:
            return True

        escalation_result = state.get("escalation_result", {})
        if escalation_result.get("escalate", False):
            return True

        return False

    def build_resolution_steps(self, intent: str) -> List[str]:
        return self.intent_steps.get(intent, self.intent_steps["general"])

    def build_resolution_summary(self, intent: str) -> str:
        return self.intent_summary.get(intent, self.intent_summary["general"])

    def process(self, state: Dict) -> Dict:
        user_input = state.get("input", "")
        intent = self.detect_intent(state)
        steps = self.build_resolution_steps(intent)
        summary = self.build_resolution_summary(intent)
        escalate = self.should_escalate(user_input, state)

        return {
            "intent": intent,
            "resolution_summary": summary,
            "resolution_steps": steps,
            "needs_escalation": escalate,
            "resolution_status": "ESCALATE" if escalate else "RESOLVED"
        }
