class InformationRetrievalAgent:
    def __init__(self, knowledge_base):
        """
        Initializes the Information Retrieval Agent.
        This agent is responsible for retrieving information from the knowledge base to answer customer questions.

        Args:
            knowledge_base: An object or connection to the knowledge base (e.g., a vector database).
        """
        self.knowledge_base = knowledge_base

    def search_knowledge_base(self, query):
        """
        Searches the knowledge base for relevant information to answer a customer's query.

        Args:
            query (str): The customer's question.

        Returns:
            list: A list of relevant documents or answers from the knowledge base.
        """
        query_words = query.lower().split()
        results = []
        
        # Simple keyword matching simulation
        # In a real system, this would use vector embeddings and a vector database.
        if isinstance(self.knowledge_base, list):
            for doc in self.knowledge_base:
                doc_lower = doc.lower()
                # Split document into words for exact word matching (tokenization)
                # We replace punctuation with spaces to ensure clean splitting
                for char in ".,?!;:":
                    doc_lower = doc_lower.replace(char, " ")
                
                doc_tokens = set(doc_lower.split())
                
                if any(word in doc_tokens for word in query_words):
                    results.append(doc)
        
        return results

    def generate_response(self, query, search_results):
        """
        Generates a response to the customer based on the search results.

        Args:
            query (str): The original customer query.
            search_results (list): The results from the search_knowledge_base method.

        Returns:
            str: A generated response to the customer.
        """
        if search_results:
            # For this prototype, we just return the first relevant result.
            # In a real system, an LLM would synthesize the answer.
            return f"Based on our knowledge base: {search_results[0]}"
        else:
            return f"I couldn't find any specific information in our knowledge base regarding '{query}'. I will forward this to a human agent."
