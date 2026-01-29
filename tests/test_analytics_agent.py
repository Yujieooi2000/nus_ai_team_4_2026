import unittest
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from agents.analytics_agent import AnalyticsAgent

class TestAnalyticsAgent(unittest.TestCase):
    def setUp(self):
        self.db = []
        self.agent = AnalyticsAgent(self.db)

    def test_log_and_insights(self):
        # Log a resolved interaction
        self.agent.log_interaction(
            {'body': 'pass'}, 
            {'category': 'billing'}, 
            {'status': 'resolved'}, 
            []
        )
        
        # Log an unresolved interaction
        self.agent.log_interaction(
            {'body': 'fail'}, 
            {'category': 'tech'}, 
            {'status': 'unresolved'}, 
            []
        )
        
        insights = self.agent.generate_insights()
        
        self.assertEqual(insights['total_requests'], 2)
        self.assertEqual(insights['resolved_count'], 1)
        self.assertEqual(insights['resolution_rate'], "50.00%")

    def test_empty_db(self):
        insights = self.agent.generate_insights()
        self.assertEqual(insights['total_requests'], 0)
        self.assertEqual(insights['resolution_rate'], 0.0)

if __name__ == '__main__':
    unittest.main()
