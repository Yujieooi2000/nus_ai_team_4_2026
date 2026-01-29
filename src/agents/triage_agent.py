class TriageAgent:
    def __init__(self):
        """
        Initializes the Triage Agent.
        This agent is responsible for the initial analysis of incoming customer requests.
        """
        pass

    def validate_input(self, text):
        """
        Checks the input text for potential security risks like prompt injection.

        Args:
            text (str): The input text to validate.

        Returns:
            bool: True if the input is considered safe, False otherwise.
        """
        suspicious_phrases = [
            "ignore previous instructions",
            "forget your instructions",
            "system prompt",
            "you are now",
            "override",
            "bypass"
        ]
        
        for phrase in suspicious_phrases:
            if phrase in text:
                return False
        return True

    def analyze_request(self, request):
        """
        Analyzes an incoming customer request to determine its category, priority, and sentiment.

        Args:
            request (dict): A dictionary containing the customer request details (e.g., 'subject', 'body', 'source').

        Returns:
            dict: A dictionary containing the analysis results (e.g., 'category', 'priority', 'sentiment', 'explanation').
        """
        text = request.get('body', '').lower()
        
        # Security Check
        if not self.validate_input(text):
            return {
                'category': 'security_alert',
                'priority': 'high',
                'sentiment': 'negative',
                'explanation': "Security alert: Potential prompt injection or malicious input detected."
            }
        
        category = 'general_inquiry'
        category_reason = "default classification"
        priority = 'low'
        priority_reason = "default priority"

        # Determine Category
        billing_keywords = ['bill', 'payment', 'invoice', 'charge', 'refund']
        tech_keywords = ['error', 'broken', 'bug', 'fail', 'crash', 'slow']
        account_keywords = ['password', 'account', 'login', 'access']
        
        for keyword in billing_keywords:
            if keyword in text:
                category = 'billing'
                category_reason = f"keyword '{keyword}' found in text"
                break
        
        if category == 'general_inquiry':
            for keyword in tech_keywords:
                if keyword in text:
                    category = 'technical_support'
                    category_reason = f"keyword '{keyword}' found in text"
                    break
        
        if category == 'general_inquiry':
            for keyword in account_keywords:
                if keyword in text:
                    category = 'account_issue'
                    category_reason = f"keyword '{keyword}' found in text"
                    break
        
        # Specific check for order status
        if 'order status' in text or 'where is my order' in text:
            category = 'order_status'
            category_reason = "phrase 'order status' or 'where is my order' found in text"

        # Determine Priority
        urgent_keywords = ['urgent', 'immediate', 'emergency', 'help', 'crash']
        for keyword in urgent_keywords:
            if keyword in text:
                priority = 'high'
                priority_reason = f"keyword '{keyword}' found in text"
                break

        explanation = f"Categorized as {category} because {category_reason}. Priority set to {priority} because {priority_reason}."

        analysis = {
            'category': category,
            'priority': priority,
            'sentiment': 'neutral', # Placeholder for sentiment analysis
            'explanation': explanation
        }
        return analysis

    def route_request(self, request, analysis):
        """
        Routes the request to the appropriate agent based on the analysis.

        Args:
            request (dict): The original customer request.
            analysis (dict): The analysis results from the analyze_request method.

        Returns:
            str: The name of the agent to which the request should be routed.
        """
        category = analysis.get('category')
        priority = analysis.get('priority')

        if category == 'security_alert':
            return 'EscalationAgent'

        # High priority items go straight to a human
        if priority == 'high':
            return 'EscalationAgent'

        if category in ['billing', 'account_issue', 'order_status']:
            return 'ResolutionAgent'
        elif category in ['technical_support', 'general_inquiry']:
            return 'InformationRetrievalAgent'
        else:
            return 'EscalationAgent'
