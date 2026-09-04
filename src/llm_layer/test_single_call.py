"""
Module 5: Single-row verification script using Google GenAI SDK.
"""

import os
from dotenv import load_dotenv
from google import genai
from google.genai import types
from src.llm_layer.prompts import SYSTEM_PROMPT

# Load GEMINI_API_KEY from .env
load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise ValueError("GEMINI_API_KEY is not set in your .env file.")

client = genai.Client(api_key=api_key)

test_payload = """
Rule ID: R3
Rule Title: RuPay Debit / Credit Card via UPI <= Rs 2,000 Zero MDR
Source Status: sourced
Statutory Authority: RBI Circular RBI/2019-20/191 & NPCI Operating Guidelines
Transaction ID: TXN_000104
Amount: Rs 1,450.00
Instrument: UPI (RuPay_credit_UPI)
Actual Fee Charged: Rs 21.75
Expected Statutory Fee: Rs 0.00
Overcharge Delta: Rs 21.75
"""

print("[InterDrift Agent] Sending test payload to Gemini...")

try:
    response = client.models.generate_content(
        model="gemini-3.6-flash",
        contents=test_payload,
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM_PROMPT,
            temperature=0.1,
            max_output_tokens=1000,
        ),
    )

    print("\n--- Model Response ---")
    if response.text:
        print(response.text.strip())

    candidate = response.candidates[0] if response.candidates else None

    print("\n--- Debug Information ---")
    print("Finish Reason:", getattr(candidate, "finish_reason", "Unknown"))
    print("Safety Ratings:", getattr(candidate, "safety_ratings", "None"))

    if hasattr(response, "usage_metadata"):
        print("Usage Metadata:", response.usage_metadata)

    print("-------------------------")
except Exception as e:
    print(f"\n[API Error] {e}")