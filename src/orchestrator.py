from agents.triage_agent import TriageAgent
from agents.information_retrieval_agent import InformationRetrievalAgent
from agents.resolution_agent import ResolutionAgent
from agents.escalation_agent import EscalationAgent
from agents.analytics_agent import AnalyticsAgent

class Orchestrator:
    def __init__(self):
        # Initialize resources (simulated)
        self.knowledge_base = [
            "Our operating hours are 9 AM to 5 PM, Monday to Friday.",
            "To reset your password, click on the 'Forgot Password' link on the login page.",
            "We accept Visa, Mastercard, and PayPal.",
            "You can track your order status in the 'My Orders' section.",
            "We offer a 30-day return policy for all unused items.",
            "Standard shipping takes 3-5 business days.",
            "You can contact our support team at support@example.com."
        ]
        self.analytics_db = []
        self.human_dashboard = self.MockDashboard()

        # Initialize Agents
        self.triage_agent = TriageAgent()
        self.info_agent = InformationRetrievalAgent(self.knowledge_base)
        self.resolution_agent = ResolutionAgent()
        self.escalation_agent = EscalationAgent(self.human_dashboard)
        self.analytics_agent = AnalyticsAgent(self.analytics_db)

    class MockDashboard:
        def create_ticket(self, request, history):
            return {'success': True, 'ticket_id': 'TKT-12345'}

    def process_request(self, user_input):
        """
        Orchestrates the handling of a user request through the multi-agent system.
        """
        request = {'body': user_input}
        conversation_history = [{'role': 'user', 'content': user_input}]

        # Step 1: Triage
        analysis = self.triage_agent.analyze_request(request)
        target_agent_name = self.triage_agent.route_request(request, analysis)

        # Step 2: Routing & Execution
        response = {}
        if target_agent_name == 'ResolutionAgent':
            response = self.resolution_agent.resolve_issue(request)
        elif target_agent_name == 'InformationRetrievalAgent':
            # Info agent needs 2 steps: search then generate
            search_results = self.info_agent.search_knowledge_base(user_input)
            response_text = self.info_agent.generate_response(user_input, search_results)
            response = {'status': 'info_provided', 'message': response_text}
        elif target_agent_name == 'EscalationAgent':
            response = self.escalation_agent.escalate_to_human(request, conversation_history)
        
        # Step 3: Analytics Logging
        self.analytics_agent.log_interaction(request, analysis, response, conversation_history)

        return {
            'agent': target_agent_name,
            'analysis': analysis,
            'response': response
        }

    def get_system_insights(self):
        return self.analytics_agent.generate_insights()
