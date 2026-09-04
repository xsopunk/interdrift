"""
Module 5: Batch Explainer Engine (Structured Outputs & Pydantic Schema)
Processes anomalous transactions in batches using Gemini 3.6 Flash.
"""

import os
import time
import pandas as pd
from pydantic import BaseModel
from dotenv import load_dotenv
from google import genai
from google.genai import types

from src.llm_layer.prompts import SYSTEM_PROMPT

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise ValueError("GEMINI_API_KEY is not set in your .env file.")

client = genai.Client(api_key=api_key)


# Strict Pydantic schema for structured output
class AuditExplanation(BaseModel):
    transaction_id: str
    explanation: str


class AuditExplanationBatch(BaseModel):
    items: list[AuditExplanation]


def format_batch_payload(rows_slice: pd.DataFrame) -> str:
    """Formats up to 5 anomaly rows into a single structured batch payload."""
    payload_lines = ["Audit Anomalies Batch:"]
    for _, row in rows_slice.iterrows():
        rule_id = str(row.get("matched_rule_id", "EXCEPTION"))
        source_status = "illustrative" if rule_id in ["R10", "R11"] else "sourced"
        
        expected_fee_raw = row.get('expected_fee')
        overcharge_raw = row.get('overcharge_amount')
        expected_fee_str = "N/A" if pd.isna(expected_fee_raw) or expected_fee_raw is None else f"Rs {float(expected_fee_raw):,.2f}"
        overcharge_str = "N/A" if pd.isna(overcharge_raw) or overcharge_raw is None else f"Rs {float(overcharge_raw):,.2f}"

        entry = (
            f"--- Entry ---\n"
            f"Transaction ID: {row.get('transaction_id')}\n"
            f"Rule ID: {rule_id}\n"
            f"Rule Title: {row.get('rule_reason', 'Automated anomaly threshold triggered.')}\n"
            f"Classification: {row.get('classification')}\n"
            f"Source Status: {source_status}\n"
            f"Amount: Rs {float(row.get('amount', 0)):,.2f}\n"
            f"Instrument: {row.get('declared_instrument')} ({row.get('sub_instrument', 'N/A')})\n"
            f"Fee Charged: Rs {float(row.get('fee_charged', 0)):,.2f}\n"
            f"Expected Fee: {expected_fee_str}\n"
            f"Overcharge Delta: {overcharge_str}\n"
        )
        payload_lines.append(entry)
    
    return "\n".join(payload_lines)


def run_explanation_pipeline(
    input_path: str = "data/processed/row_level_results.csv",
    output_path: str = "data/processed/row_level_results_with_explanations.csv",
    sample_limit: int = 5,
    batch_size: int = 5
):
    print(f"[InterDrift Explainer] Loading audit results from {input_path}...")
    df = pd.read_csv(input_path)

    if "explanation" not in df.columns:
        df["explanation"] = ""

    anomalies_mask = df["classification"].isin(["Leaked", "Exception", "Flagged_For_Review"])
    target_indices = df[anomalies_mask].index.tolist()

    if sample_limit:
        target_indices = target_indices[:sample_limit]

    total_targets = len(target_indices)
    print(f"[InterDrift Explainer] Processing {total_targets} anomalies in batches of {batch_size}...")

    # Set thinking_level to LOW to minimize token overhead and expand token cap
    gen_config = types.GenerateContentConfig(
        system_instruction=SYSTEM_PROMPT,
        max_output_tokens=4000,
        response_mime_type="application/json",
        response_schema=AuditExplanationBatch,
        thinking_config=types.ThinkingConfig(thinking_level="LOW"),
        automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),
    )

    start_time = time.time()
    processed_count = 0

    for i in range(0, total_targets, batch_size):
        batch_idx_chunk = target_indices[i : i + batch_size]
        batch_df = df.loc[batch_idx_chunk]
        batch_payload = format_batch_payload(batch_df)

        print(f"  -> Sending batch [{i+1} to {min(i + batch_size, total_targets)}] to Gemini Flash...")
        try:
            response = client.models.generate_content(
                model="gemini-3.6-flash",
                contents=batch_payload,
                config=gen_config,
            )

            if response.text:
                parsed_batch = AuditExplanationBatch.model_validate_json(response.text)
                for item in parsed_batch.items:
                    matched_row = df[df["transaction_id"] == item.transaction_id]
                    if not matched_row.empty:
                        df.at[matched_row.index[0], "explanation"] = item.explanation
                        processed_count += 1
            else:
                print(f"     [Warning] Received empty response for batch.")

        except Exception as e:
            print(f"     [Batch Warning] Failed batch processing: {e}")
            for row_idx in batch_idx_chunk:
                df.at[row_idx, "explanation"] = "Audit Note: Flagged for manual merchant controller review."

        time.sleep(0.5)

    df.to_csv(output_path, index=False)
    elapsed = time.time() - start_time
    print(f"\n[InterDrift Explainer] Completed! {processed_count}/{total_targets} explanations saved in {elapsed:.2f}s.")


if __name__ == "__main__":
    # Process all anomalous rows in batches of 5
    run_explanation_pipeline(sample_limit=None, batch_size=5)