from typing import List, Dict, Any
from dataclasses import dataclass
import json
from openai import OpenAI

# -------------------------------
# Data Models
# -------------------------------

@dataclass
class VerificationResult:
    is_factual: bool
    hallucination_detected: bool
    unsupported_claims: List[str]
    confidence_score: float
    recommendation: str
    reasoning: str


# -------------------------------
# Verification Agent
# -------------------------------

class VerificationAgent:

    def __init__(self, api_key: str, model: str = "gpt-4o-mini"):
        self.client = OpenAI(api_key=api_key)
        self.model = model

    def verify(
            self,
            user_query: str,
            retrieved_docs: List[str],
            generated_answer: str
    ) -> VerificationResult:

        verification_prompt = self._build_prompt(
            user_query,
            retrieved_docs,
            generated_answer
        )

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are a strict AI verification critic."},
                {"role": "user", "content": verification_prompt}
            ],
            temperature=0
        )

        result_json = self._safe_parse(response.choices[0].message.content)

        return VerificationResult(
            is_factual=result_json.get("is_factual", False),
            hallucination_detected=result_json.get("hallucination_detected", True),
            unsupported_claims=result_json.get("unsupported_claims", []),
            confidence_score=result_json.get("confidence_score", 0.0),
            recommendation=result_json.get("recommendation", "ESCALATE"),
            reasoning=result_json.get("reasoning", "")
        )

    # -------------------------------
    # Prompt Builder
    # -------------------------------

    def _build_prompt(
            self,
            query: str,
            docs: List[str],
            answer: str
    ) -> str:

        docs_text = "\n\n".join(
            [f"Document {i+1}:\n{doc}" for i, doc in enumerate(docs)]
        )

        return f"""
You are a Verification Agent in an enterprise AI system.

Your task:
Evaluate whether the generated answer is fully supported by the retrieved documents.

USER QUERY:
{query}

RETRIEVED DOCUMENTS:
{docs_text}

GENERATED ANSWER:
{answer}

Tasks:
1. Identify hallucinations (claims not supported by docs)
2. Identify factual inconsistencies
3. List unsupported claims explicitly
4. Provide confidence score between 0 and 1
5. Recommend one:
   - APPROVE
   - REVISE
   - ESCALATE

Return STRICT JSON format:

{{
  "is_factual": true/false,
  "hallucination_detected": true/false,
  "unsupported_claims": [],
  "confidence_score": float,
  "recommendation": "APPROVE | REVISE | ESCALATE",
  "reasoning": "brief explanation"
}}
"""

    # -------------------------------
    # Safe JSON Parsing
    # -------------------------------

    def _safe_parse(self, content: str) -> Dict[str, Any]:
        try:
            return json.loads(content)
        except Exception:
            return {
                "is_factual": False,
                "hallucination_detected": True,
                "unsupported_claims": ["Parsing failure"],
                "confidence_score": 0.0,
                "recommendation": "ESCALATE",
                "reasoning": "LLM response parsing failed"
            }