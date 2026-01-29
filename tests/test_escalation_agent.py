import unittest
from unittest.mock import MagicMock
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from agents.escalation_agent import EscalationAgent

class TestEscalationAgent(unittest.TestCase):
    def setUp(self):
        self.mock_dashboard = MagicMock()
        self.agent = EscalationAgent(self.mock_dashboard)

    def test_escalate_success(self):
        self.mock_dashboard.create_ticket.return_value = {'success': True, 'ticket_id': 'TKT-101'}
        
        request = {'body': 'Help!'}
        history = [{'role': 'user', 'content': 'Help!'}]
        
        result = self.agent.escalate_to_human(request, history)
        
        self.assertEqual(result['status'], 'escalated')
        self.assertEqual(result['ticket_id'], 'TKT-101')
        self.assertIn("TKT-101", result['message'])
        self.mock_dashboard.create_ticket.assert_called_once()

    def test_escalate_failure(self):
        self.mock_dashboard.create_ticket.return_value = {'success': False}
        
        result = self.agent.escalate_to_human({}, [])
        
        self.assertEqual(result['status'], 'escalation_failed')
        self.assertIn("unable to escalate", result['message'])

if __name__ == '__main__':
    unittest.main()
