import unittest
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from agents.resolution_agent import ResolutionAgent

class TestResolutionAgent(unittest.TestCase):
    def setUp(self):
        self.agent = ResolutionAgent()

    def test_resolve_password_reset(self):
        request = {'body': "I forgot my password and need a reset."}
        resolution = self.agent.resolve_issue(request)
        self.assertEqual(resolution['status'], 'resolved')
        self.assertIn("password reset link", resolution['message'])

    def test_resolve_refund(self):
        request = {'body': "I would like a refund for my last order."}
        resolution = self.agent.resolve_issue(request)
        self.assertEqual(resolution['status'], 'resolved')
        self.assertIn("refund request has been processed", resolution['message'])

    def test_unresolved_issue(self):
        request = {'body': "My internet is slow."}
        resolution = self.agent.resolve_issue(request)
        self.assertEqual(resolution['status'], 'unresolved')
        self.assertIn("unable to resolve", resolution['message'])

if __name__ == '__main__':
    unittest.main()
