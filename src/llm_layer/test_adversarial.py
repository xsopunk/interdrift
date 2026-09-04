"""
Module 5: Adversarial verification script.
Tests illustrative benchmark rules and missing-tag exception scenarios.
"""

import os
from dotenv import load_dotenv
from google import genai
from google.genai import types
from src.llm_layer.prompts import SYSTEM_PROMPT

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

cases = {
    "Case 1 (Illustrative Rule)": """
Rule ID: R10
Rule Title: Commercial / Corporate Card L2/L3 Downgrade Surcharge
Source Status: illustrative
Statutory Authority: Network Wholesale Benchmark Matrix
Transaction ID: TXN_000305
Amount: Rs 85,000.00
Instrument: Card (Credit_corporate)
Actual Fee Charged: Rs 2,380.00
Expected Statutory Fee: Rs 1,700.00
Overcharge Delta: Rs 680.00
Additional Context: Missing tax amount and PO reference caused downgrade penalty.
""",
    "Case 2 (Missing Tag Exception)": """
Rule ID: EXCEPTION
Rule Title: Unclassifiable Missing Sub-Instrument Tag
Source Status: sourced
Statutory Authority: Settlement Data Integrity Standards
Transaction ID: TXN_000412
Amount: Rs 3,200.00
Instrument: Unknown (sub_instrument field is blank)
Actual Fee Charged: Rs 48.00
Expected Statutory Fee: Rs 0.00
Overcharge Delta: Rs 0.00
Additional Context: Sub-instrument tag omitted by payment aggregator feed.
"""
}

for name, payload in cases.items():
    print(f"\n================ {name} ================")
    response = client.models.generate_content(
        model="gemini-3.6-flash",
        contents=payload,
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM_PROMPT,
            temperature=0.1,
            max_output_tokens=1200,
        ),
    )
    if response.text:
        print(response.text.strip())