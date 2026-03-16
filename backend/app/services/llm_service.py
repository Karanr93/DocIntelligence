"""LLM Service for clause extraction using AWS Bedrock, Groq, OpenAI, or Ollama."""
import json
from typing import Optional
from app.config import settings


EXTRACTION_PROMPT = """You are a document clause extraction expert. Analyze the following page text and determine if it contains content related to the category "{category}".

RULES:
1. Only extract information that ACTUALLY exists in the text. Do NOT hallucinate or infer.
2. If the text does not contain relevant content for this category, return is_relevant: false.
3. For each relevant section found, extract the verbatim text and provide structured metadata.
4. Rate your confidence from 0.0 to 1.0 based on how clearly the text relates to the category.

CATEGORY DEFINITION:
- Medical: Any content about health, medical procedures, patient care, diagnoses, treatments, healthcare policies, insurance claims, medications.
- Finance: Any content about financial matters, investments, revenue, budgets, taxes, loans, monetary policies, fiscal data.
- Sports: Any content about athletic activities, competitions, teams, players, tournaments, training, sports contracts, endorsements.

PAGE TEXT:
---
{text}
---

Respond ONLY in this exact JSON format (no markdown, no explanation):
{{
  "is_relevant": true/false,
  "confidence": 0.0-1.0,
  "extracted_sections": [
    {{
      "text": "exact verbatim quote from the page",
      "summary": "one-line structured summary",
      "metadata": {{
        "entities": ["list of key entities mentioned"],
        "dates": ["any dates found"],
        "amounts": ["any monetary amounts"],
        "key_terms": ["important domain terms"]
      }}
    }}
  ],
  "reasoning": "brief explanation of why this is/isn't relevant"
}}"""

SYSTEM_PROMPT = "You are a precise document analysis assistant. Never fabricate information. Only extract what exists in the text."


class LLMService:
    """Handles LLM calls for clause extraction with hallucination guards."""

    def __init__(self):
        self.provider = settings.llm_provider
        self.model = settings.llm_model

    def _call_bedrock(self, system_prompt, user_prompt):
        """Call AWS Bedrock with Claude Sonnet."""
        import boto3

        client = boto3.client(
            "bedrock-runtime",
            aws_access_key_id=settings.aws_access_key_id,
            aws_secret_access_key=settings.aws_secret_access_key,
            region_name=settings.bedrock_region
        )

        body = json.dumps({
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 2000,
            "temperature": 0.1,
            "system": system_prompt,
            "messages": [
                {"role": "user", "content": user_prompt}
            ]
        })

        response = client.invoke_model(
            modelId=self.model,
            contentType="application/json",
            accept="application/json",
            body=body
        )

        result = json.loads(response["body"].read())
        return result["content"][0]["text"]

    def _call_ollama(self, system_prompt, user_prompt):
        """Call Ollama local LLM (OpenAI-compatible API)."""
        from openai import OpenAI
        client = OpenAI(
            base_url=settings.ollama_base_url,
            api_key="ollama"  # Ollama doesn't need a real key
        )

        response = client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.1,
            max_tokens=2000
        )
        return response.choices[0].message.content.strip()

    def _call_groq_or_openai(self, system_prompt, user_prompt):
        """Call Groq or OpenAI API."""
        if self.provider == "groq":
            from groq import Groq
            client = Groq(api_key=settings.groq_api_key)
        else:
            from openai import OpenAI
            client = OpenAI(api_key=settings.openai_api_key)

        response = client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.1,
            max_tokens=2000
        )
        return response.choices[0].message.content.strip()

    def extract_clause(self, text, category_name):
        """
        Use LLM to extract and classify clause content.
        Returns structured extraction result with confidence score.
        """
        if not text.strip():
            return {"is_relevant": False, "confidence": 0.0, "extracted_sections": [], "reasoning": "Empty text"}

        # Truncate very long texts to stay within token limits
        max_chars = 6000
        truncated = text[:max_chars] if len(text) > max_chars else text

        prompt = EXTRACTION_PROMPT.format(category=category_name, text=truncated)

        try:
            # Call the appropriate provider
            if self.provider == "bedrock":
                content = self._call_bedrock(SYSTEM_PROMPT, prompt)
            elif self.provider == "ollama":
                content = self._call_ollama(SYSTEM_PROMPT, prompt)
            else:
                content = self._call_groq_or_openai(SYSTEM_PROMPT, prompt)

            # Parse JSON from response (handle markdown code blocks)
            if content.startswith("```"):
                content = content.split("```")[1]
                if content.startswith("json"):
                    content = content[4:]
            content = content.strip()

            result = json.loads(content)

            # Hallucination guard: verify extracted text exists in original
            if result.get("is_relevant") and result.get("extracted_sections"):
                verified_sections = []
                for section in result["extracted_sections"]:
                    extracted = section.get("text", "")
                    # Check if at least 60% of words from extraction exist in original
                    words = extracted.lower().split()
                    if words:
                        match_count = sum(1 for w in words if w in text.lower())
                        match_ratio = match_count / len(words)
                        if match_ratio >= 0.6:
                            verified_sections.append(section)
                        else:
                            # Penalize confidence for hallucinated content
                            result["confidence"] = max(0.2, result.get("confidence", 0) - 0.3)

                result["extracted_sections"] = verified_sections
                if not verified_sections:
                    result["is_relevant"] = False
                    result["confidence"] = 0.1
                    result["reasoning"] = "Extracted content could not be verified in source text"

            return result

        except json.JSONDecodeError:
            return {
                "is_relevant": False,
                "confidence": 0.0,
                "extracted_sections": [],
                "reasoning": "LLM response was not valid JSON"
            }
        except Exception as e:
            return {
                "is_relevant": False,
                "confidence": 0.0,
                "extracted_sections": [],
                "reasoning": f"LLM call failed: {str(e)}"
            }


llm_service = LLMService()
