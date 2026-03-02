import re
import math
from typing import List, Dict, Any
from dataclasses import dataclass
from collections import Counter


@dataclass
class RetrievalResult:
    retrieved_docs: List[str]
    scores: List[float]
    confidence_score: float
    explanation: str


class InformationRetrievalAgent:

    def __init__(self, knowledge_base: List[str], top_k: int = 3):
        self.knowledge_base = knowledge_base
        self.top_k = top_k

    # ----------------------------------
    # Text Processing
    # ----------------------------------

    def _tokenize(self, text: str) -> List[str]:
        text = text.lower()
        text = re.sub(r"[^\w\s]", " ", text)
        return text.split()

    # ----------------------------------
    # TF-IDF Like Similarity (Lightweight)
    # ----------------------------------

    def _compute_similarity(self, query_tokens, doc_tokens):
        query_counter = Counter(query_tokens)
        doc_counter = Counter(doc_tokens)

        intersection = set(query_counter.keys()) & set(doc_counter.keys())
        numerator = sum(query_counter[x] * doc_counter[x] for x in intersection)

        query_norm = math.sqrt(sum(v**2 for v in query_counter.values()))
        doc_norm = math.sqrt(sum(v**2 for v in doc_counter.values()))

        if query_norm == 0 or doc_norm == 0:
            return 0.0

        return numerator / (query_norm * doc_norm)

    # ----------------------------------
    # Retrieval
    # ----------------------------------

    def search_knowledge_base(self, query: str) -> RetrievalResult:

        query_tokens = self._tokenize(query)
        scored_docs = []

        for doc in self.knowledge_base:
            doc_tokens = self._tokenize(doc)
            score = self._compute_similarity(query_tokens, doc_tokens)
            if score > 0:
                scored_docs.append((doc, score))

        # Sort by similarity score
        scored_docs.sort(key=lambda x: x[1], reverse=True)

        top_docs = scored_docs[:self.top_k]
        retrieved_docs = [doc for doc, _ in top_docs]
        scores = [round(score, 4) for _, score in top_docs]

        confidence_score = sum(scores) / len(scores) if scores else 0.0

        explanation = (
            f"Retrieved top {len(retrieved_docs)} documents "
            f"ranked by cosine similarity. "
            f"Average similarity score: {confidence_score:.2f}"
        )

        return RetrievalResult(
            retrieved_docs=retrieved_docs,
            scores=scores,
            confidence_score=confidence_score,
            explanation=explanation
        )

    # ----------------------------------
    # Response Generation (Grounded)
    # ----------------------------------

    def generate_response(
        self,
        query: str,
        retrieval_result: RetrievalResult
    ) -> Dict[str, Any]:

        if not retrieval_result.retrieved_docs:
            return {
                "answer": None,
                "confidence_score": 0.0,
                "requires_escalation": True,
                "explanation": "No relevant documents found."
            }

        # Grounded response (No hallucination)
        synthesized_answer = "\n\n".join(
            f"[Source {i+1}] {doc}"
            for i, doc in enumerate(retrieval_result.retrieved_docs)
        )

        final_answer = (
            f"Based on our knowledge base:\n\n{synthesized_answer}"
        )

        requires_escalation = retrieval_result.confidence_score < 0.25

        return {
            "answer": final_answer,
            "confidence_score": retrieval_result.confidence_score,
            "requires_escalation": requires_escalation,
            "retrieved_docs": retrieval_result.retrieved_docs,
            "similarity_scores": retrieval_result.scores,
            "explanation": retrieval_result.explanation
        }
