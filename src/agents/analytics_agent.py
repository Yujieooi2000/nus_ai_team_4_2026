class AnalyticsAgent:
    def __init__(self, analytics_database):
        """
        Initializes the Analytics Agent.
        This agent is responsible for monitoring the performance of the support system and identifying trends.

        Args:
            analytics_database: An object or connection to the analytics database.
        """
        self.analytics_database = analytics_database

    def log_interaction(self, request, analysis, resolution, conversation_history):
        """
        Logs the details of a customer interaction to the analytics database.

        Args:
            request (dict): The original customer request.
            analysis (dict): The analysis from the Triage Agent.
            resolution (dict): The resolution from the Resolution Agent or other agents.
            conversation_history (list): The full conversation history.
        """
        log_entry = {
            'timestamp': '2026-01-05T18:00:00', # Placeholder for actual timestamp
            'request': request,
            'analysis': analysis,
            'resolution': resolution,
            'history': conversation_history
        }
        
        # In this prototype, we assume analytics_database is a list acting as an in-memory store.
        if isinstance(self.analytics_database, list):
            self.analytics_database.append(log_entry)

    def generate_insights(self):
        """
        Analyzes the collected data to generate insights and identify trends.

        Returns:
            dict: A dictionary containing insights and trend data.
        """
        if not isinstance(self.analytics_database, list) or not self.analytics_database:
            return {
                'total_requests': 0,
                'resolved_count': 0,
                'resolution_rate': 0.0,
                'category_breakdown': {}
            }

        total_requests = len(self.analytics_database)
        resolved_count = sum(1 for entry in self.analytics_database 
                             if entry.get('resolution', {}).get('status') == 'resolved')
        
        resolution_rate = (resolved_count / total_requests) * 100

        # Calculate category breakdown
        category_counts = {}
        for entry in self.analytics_database:
            category = entry.get('analysis', {}).get('category', 'unknown')
            category_counts[category] = category_counts.get(category, 0) + 1

        insights = {
            'total_requests': total_requests,
            'resolved_count': resolved_count,
            'resolution_rate': f"{resolution_rate:.2f}%",
            'category_breakdown': category_counts
        }
        return insights
