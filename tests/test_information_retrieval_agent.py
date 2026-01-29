import unittest
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from agents.information_retrieval_agent import InformationRetrievalAgent

class TestInformationRetrievalAgent(unittest.TestCase):
    def setUp(self):
        # Mock knowledge base
        self.kb = [
            "Our operating hours are 9 AM to 5 PM, Monday to Friday.",
            "To reset your password, click on the 'Forgot Password' link on the login page.",
            "We accept Visa, Mastercard, and PayPal."
        ]
        self.agent = InformationRetrievalAgent(self.kb)

    def test_search_success(self):
        query = "What are your hours?"
        results = self.agent.search_knowledge_base(query)
        self.assertTrue(len(results) > 0)
        self.assertIn("Our operating hours are 9 AM to 5 PM, Monday to Friday.", results)

    def test_search_no_results(self):
        query = "Do you sell spaceships?"
        results = self.agent.search_knowledge_base(query)
        self.assertEqual(len(results), 0)

    def test_generate_response_success(self):
        query = "hours"
        results = ["Our operating hours are 9 AM to 5 PM, Monday to Friday."]
        response = self.agent.generate_response(query, results)
        self.assertIn("Based on our knowledge base", response)
        self.assertIn("9 AM to 5 PM", response)

    def test_generate_response_failure(self):
        query = "aliens"
        results = []
        response = self.agent.generate_response(query, results)
        self.assertIn("I couldn't find any specific information", response)

if __name__ == '__main__':
    unittest.main()
