class EscalationAgent:
    def __init__(self, human_agent_dashboard):
        """
        Initializes the Escalation Agent.
        This agent is responsible for escalating issues to human agents.

        Args:
            human_agent_dashboard: An object or connection to the human agent dashboard.
        """
        self.human_agent_dashboard = human_agent_dashboard

    def escalate_to_human(self, request, conversation_history):
        """
        Escalates a customer's issue to a human agent.

        Args:
            request (dict): The original customer request.
            conversation_history (list): A list of the interactions between the customer and the AI agents.

        Returns:
            dict: A dictionary containing the escalation status and a message to the customer.
        """
        # Call the dashboard service to create a ticket
        try:
            result = self.human_agent_dashboard.create_ticket(
                request=request,
                history=conversation_history
            )
            
            if result.get('success'):
                ticket_id = result.get('ticket_id', 'UNKNOWN')
                return {
                    'status': 'escalated',
                    'ticket_id': ticket_id,
                    'message': f"I've escalated your request to a human agent (Ticket ID: {ticket_id}). They will get back to you shortly."
                }
            else:
                return {
                    'status': 'escalation_failed',
                    'message': "I'm sorry, but I was unable to escalate your request at this time due to a technical issue."
                }
        except Exception as e:
            return {
                'status': 'escalation_failed',
                'message': f"An error occurred during escalation: {str(e)}"
            }
