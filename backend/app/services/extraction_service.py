"""LLM-based extraction service for incident data."""
import os
import requests
import json
from typing import Optional, Dict, List
from datetime import datetime


class ExtractionService:
    """Service for extracting structured incident data from unstructured text using LM Studio."""

    def __init__(self):
        # Use LM Studio endpoint (OpenAI-compatible API)
        self.lm_studio_url = os.getenv("LM_STUDIO_URL", "http://192.168.0.179:1234")
        self.api_endpoint = f"{self.lm_studio_url}/v1/chat/completions"

    def ensure_model_loaded(self) -> bool:
        """Check if LM Studio is accessible."""
        try:
            # Try to connect to LM Studio
            response = requests.get(f"{self.lm_studio_url}/v1/models", timeout=5)
            return response.status_code == 200
        except Exception as e:
            print(f"Error connecting to LM Studio: {str(e)}")
            return False

    def extract_incidents_from_text(self, text: str, source_url: str) -> List[Dict]:
        """
        Extract structured incident data from article text.

        Returns a list of incidents found in the text, each with:
        - title: Brief description of the incident
        - what_happened: Detailed description
        - actors: List of people/organizations involved (perpetrators)
        - victims: List of victims/targets
        - location: Where it happened
        - date: When it happened
        - laws_violated: List of laws/rights violated
        - evidence: Types of evidence mentioned
        """

        system_message = """You are an expert at extracting government accountability incidents from news articles.
You extract structured data about government misconduct, abuse of power, rights violations, or illegal actions.
You return ONLY valid JSON arrays, no additional text."""

        user_message = f"""Read the following article and extract ALL distinct incidents of government misconduct, abuse of power, rights violations, or illegal actions.

For EACH incident, extract:
1. **title**: A brief, specific description (e.g., "ICE agent shot protester with rubber bullet")
2. **what_happened**: Detailed description of what occurred
3. **actors**: Names and roles of government officials/agents who committed the act (e.g., ["Agent John Doe, ICE", "Officer Jane Smith, NYPD"])
4. **victims**: Names of victims/targets if mentioned
5. **location**: Specific location (city, state)
6. **date**: Date or time period when it occurred
7. **laws_violated**: Specific laws, amendments, or rights violated (e.g., ["4th Amendment", "Use of force policy"])
8. **evidence**: Types of evidence mentioned (e.g., ["body camera footage", "witness testimony", "court documents"])

Return ONLY a JSON array of incidents. Each incident must be a separate object. If no incidents are found, return an empty array [].

Example format:
[
  {{
    "title": "ICE agent detained US citizen without warrant",
    "what_happened": "ICE Agent John Doe detained Maria Garcia, a US citizen, for 48 hours without a warrant during a raid at her home.",
    "actors": ["Agent John Doe, ICE"],
    "victims": ["Maria Garcia, US citizen"],
    "location": "Chicago, IL",
    "date": "2024-01-15",
    "laws_violated": ["4th Amendment - unreasonable search and seizure"],
    "evidence": ["detention records", "witness statements"]
  }}
]

Article text:
{text[:8000]}

Source: {source_url}

Return the JSON array now:"""

        try:
            # Call LM Studio API (OpenAI-compatible)
            response = requests.post(
                self.api_endpoint,
                json={
                    "messages": [
                        {"role": "system", "content": system_message},
                        {"role": "user", "content": user_message}
                    ],
                    "temperature": 0.1,  # Low temperature for factual extraction
                    "max_tokens": 4000
                },
                timeout=120  # LM Studio with GPU should be much faster
            )

            if response.status_code != 200:
                print(f"LM Studio API error: {response.status_code} - {response.text}")
                return []

            result = response.json()

            # Extract content from OpenAI-compatible response
            if "choices" in result and len(result["choices"]) > 0:
                response_text = result["choices"][0]["message"]["content"]
            else:
                print(f"Unexpected response format: {result}")
                return []

            # Parse JSON response
            try:
                # Clean response text (remove markdown code blocks if present)
                response_text = response_text.strip()
                if response_text.startswith("```json"):
                    response_text = response_text[7:]
                if response_text.startswith("```"):
                    response_text = response_text[3:]
                if response_text.endswith("```"):
                    response_text = response_text[:-3]
                response_text = response_text.strip()

                incidents = json.loads(response_text)

                # Handle both array and object with array
                if isinstance(incidents, dict) and "incidents" in incidents:
                    incidents = incidents["incidents"]

                if not isinstance(incidents, list):
                    print(f"Expected list, got: {type(incidents)}")
                    return []

                return incidents
            except json.JSONDecodeError as e:
                print(f"JSON decode error: {str(e)}")
                print(f"Response text: {response_text[:500]}")
                return []

        except requests.exceptions.Timeout:
            print("LM Studio request timed out")
            return []
        except Exception as e:
            print(f"Error extracting incidents: {str(e)}")
            return []

    def extract_from_queue_item(self, queue_item) -> List[Dict]:
        """
        Extract incidents from an ingestion queue item.

        Args:
            queue_item: IngestionQueue model instance with raw_content and source_url

        Returns:
            List of extracted incident dictionaries
        """
        if not queue_item.raw_content:
            print(f"No raw_content for queue item {queue_item.id}")
            return []

        # Ensure model is loaded
        if not self.ensure_model_loaded():
            print("Failed to load LLM model")
            return []

        return self.extract_incidents_from_text(
            text=queue_item.raw_content,
            source_url=queue_item.source_url
        )
