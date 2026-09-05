"""
Module 1 : Synthetic Settlement Data Generator
Simulates Indian merchant payment records with injected fee leakage,
L2/L3 data degradation, and classification exceptions.
Configurable via API or direct function import, while maintaining standalone CLI execution.
"""

import json
import os
import random
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

import pandas as pd
from faker import Faker

fake = Faker("en_IN")

# Realistic Indian Merchant Rail Distribution
INSTRUMENT_WEIGHTS = {
    "bank_UPI": 0.52,
    "RuPay_debit": 0.15,
    "RuPay_credit_UPI": 0.10,
    "PPI_wallet_UPI": 0.08,
    "Visa_credit": 0.07,
    "Mastercard_credit": 0.05,
    "Debit_non_rupay": 0.03,
}

BIN_TIER_MAPPING = {
    "411111": ("Visa", "basic"),
    "422222": ("Visa", "premium_rewards"),
    "433333": ("Visa", "corporate"),
    "511111": ("Mastercard", "basic"),
    "522222": ("Mastercard", "premium_rewards"),
    "533333": ("Mastercard", "corporate"),
    "607111": ("RuPay", "basic"),
    "607222": ("RuPay", "corporate"),
}

MCC_DIRECTORY = {
    "retail": "5411",         # Grocery/Supermarket
    "education": "8220",      # Colleges/Universities
    "B2B wholesale": "5045",  # Computers/Software/Office equipment
    "restaurant": "5812",     # Eating places
}

GST_RATE = 0.18


def generate_msa(config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Generates a synthetic Merchant Service Agreement specification dictionary.
    
    Accepts optional configurable fields:
    - merchant_id (str)
    - merchant_name (str)
    - registered_business_type (str)
    - expected_mcc (str)
    - annual_turnover_tier (str: 'below_20L' | 'above_20L')
    - cards_flat_blended (float)
    - tax_rate_gst (float)
    """
    cfg = config or {}
    business_type = cfg.get("registered_business_type") or cfg.get("business_category") or "B2B wholesale"
    expected_mcc = cfg.get("expected_mcc") or MCC_DIRECTORY.get(business_type, "5045")
    cards_flat = float(cfg.get("cards_flat_blended") or cfg.get("contracted_flat_rate") or 0.02)
    turnover_tier = cfg.get("annual_turnover_tier") or cfg.get("turnover_tier") or "above_20L"

    return {
        "merchant_id": cfg.get("merchant_id", "MID_IND_99214"),
        "merchant_name": cfg.get("merchant_name", "Sagar Retail Enterprises"),
        "registered_business_type": business_type,
        "expected_mcc": expected_mcc,
        "annual_turnover_tier": turnover_tier,
        "pricing_model": cfg.get("pricing_model", "blended_mdr"),
        "contracted_rates": {
            "upi_standard": float(cfg.get("upi_standard", 0.0)),
            "rupay_debit": float(cfg.get("rupay_debit", 0.0)),
            "cards_flat_blended": cards_flat,
            "rupay_credit_upi_flat": float(cfg.get("rupay_credit_upi_flat", 0.018)),
            "wallet_ppi_flat": float(cfg.get("wallet_ppi_flat", 0.018)),
        },
        "tax_rate_gst": float(cfg.get("tax_rate_gst", GST_RATE)),
    }


def calculate_expected_fee(sub_instrument: str, amount: float, turnover_tier: str, mcc: str) -> float:
    """Computes statutory/regulatory base MDR fee before GST."""
    if not sub_instrument:
        return 0.0

    # R1: Bank UPI = 0%
    if sub_instrument == "bank_UPI":
        return 0.0

    # R2: RuPay Debit = 0%
    if sub_instrument == "RuPay_debit":
        return 0.0

    # R3 & R4: RuPay Credit on UPI (threshold ₹2,000)
    if sub_instrument == "RuPay_credit_UPI":
        if amount <= 2000.0:
            return 0.0
        # Typical merchant interchange slab above 2k (~1.5%)
        return round(amount * 0.015, 2)

    # R5 & R6: PPI / Wallet on UPI (threshold ₹2,000)
    if sub_instrument == "PPI_wallet_UPI":
        if amount <= 2000.0:
            return 0.0
        # NPCI tiered slab: Education/Utilities ~0.7%, Retail/Standard ~1.1%
        rate = 0.007 if mcc == "8220" else 0.011
        return round(amount * rate, 2)

    # R7 & R8: Non-RuPay Debit Card (RBI 2017 circular caps)
    if sub_instrument == "Debit_non_rupay":
        if turnover_tier == "below_20L":
            return min(round(amount * 0.004, 2), 200.0)
        else:
            return min(round(amount * 0.009, 2), 1000.0)

    # R9: Standard Commercial/Retail Credit Cards (Market / contracted rate default: 2%)
    if "credit" in sub_instrument:
        return round(amount * 0.02, 2)

    return 0.0


def generate_transaction(
    tx_id: int,
    start_date: datetime,
    msa: dict,
    min_amount: float = 50.0,
    max_amount: float = 100000.0,
    rates: Optional[Dict[str, float]] = None,
) -> dict:
    """Generates an individual transaction dictionary with simulated fields and anomalies."""
    rates = rates or {}
    rupay_credit_leak_rate = rates.get("rupay_credit_leak_rate", 0.15)
    l2_l3_downgrade_rate = rates.get("l2_l3_downgrade_rate", 0.12)
    mcc_misclass_rate = rates.get("mcc_misclass_rate", 0.10)
    exception_rate = rates.get("exception_rate", 0.05)

    timestamp = start_date + timedelta(
        days=random.randint(0, 14),
        hours=random.randint(0, 23),
        minutes=random.randint(0, 59),
        seconds=random.randint(0, 59)
    )

    # 1. Realistic amount distribution (skewed towards small tickets for UPI)
    sub_inst = random.choices(
        list(INSTRUMENT_WEIGHTS.keys()),
        weights=list(INSTRUMENT_WEIGHTS.values()),
        k=1
    )[0]

    # Calculate amount within specified min/max bounds
    effective_min = max(1.0, float(min_amount))
    effective_max = max(effective_min, float(max_amount))

    if "UPI" in sub_inst:
        declared_inst = "UPI"
        if effective_max <= 2000.0:
            amount = round(random.uniform(effective_min, effective_max), 2)
        else:
            # Distribute between low-ticket and high-ticket
            ticket_choice = random.random()
            if ticket_choice < 0.65:
                amt = random.uniform(effective_min, min(2000.0, effective_max))
            else:
                amt = random.uniform(max(2000.01, effective_min), effective_max)
            amount = round(amt, 2)
    else:
        declared_inst = "Card"
        amount = round(random.uniform(effective_min, effective_max), 2)

    # 2. Metadata & BIN assignment
    card_bin = ""
    card_tier = "N/A"
    if "credit" in sub_inst or "debit" in sub_inst:
        card_bin = random.choice(list(BIN_TIER_MAPPING.keys()))
        _, card_tier = BIN_TIER_MAPPING[card_bin]

    # 3. Establish base fields
    merchant_category = msa.get("registered_business_type", "B2B wholesale")
    mcc = msa.get("expected_mcc", "5045")
    turnover_tier = msa.get("annual_turnover_tier", "above_20L")
    contracted_rates = msa.get("contracted_rates", {})
    contracted_flat_rate = contracted_rates.get("cards_flat_blended", 0.02)

    # L2/L3 commercial data fields
    tax_amount_provided = True
    po_code_provided = True
    line_item_provided = True if amount > 10000 else False

    expected_base_fee = calculate_expected_fee(sub_inst, amount, turnover_tier, mcc)
    fee_charged = expected_base_fee
    injected_issue = "clean"

    # 4. Inject intentional anomalies using configured rates
    roll = random.random()

    # Anomaly E: Sub-instrument missing (Unclassifiable Exception)
    if roll < exception_rate:
        sub_inst = ""  # Left blank to simulate missing tag from raw aggregator feed
        injected_issue = "exception_missing_tag"

    # Anomaly A: Zero-MDR Leakage (RuPay credit or PPI <= ₹2,000 charged fee)
    elif sub_inst in ["RuPay_credit_UPI", "PPI_wallet_UPI"] and amount <= 2000.0 and random.random() < rupay_credit_leak_rate:
        fee_charged = round(amount * 0.015, 2)
        injected_issue = "R3_R5_zero_rate_leak"

    # Anomaly B: Non-RuPay Debit cap breach (RBI ₹1,000 cap ignored on large tickets)
    elif sub_inst == "Debit_non_rupay" and amount > 100000.0 and random.random() < 0.25:
        fee_charged = round(amount * 0.009, 2)  # Exceeds ₹1,000 cap
        injected_issue = "R8_debit_cap_breach"

    # Anomaly C: L2/L3 Downgrade on Corporate Cards (R10)
    elif card_tier == "corporate" and random.random() < l2_l3_downgrade_rate:
        tax_amount_provided = False
        po_code_provided = False
        fee_charged = round(expected_base_fee + (amount * 0.008), 2)  # 80 bps downgrade penalty
        injected_issue = "R10_l2_l3_downgrade"

    # Anomaly D: MCC Misclassification (R12)
    elif random.random() < mcc_misclass_rate:
        mcc = "5411" if msa.get("expected_mcc") != "5411" else "5045"
        injected_issue = "R12_mcc_misclassification"

    tax_charged = round(fee_charged * GST_RATE, 2)

    return {
        "transaction_id": f"TXN_{tx_id:06d}",
        "timestamp": timestamp.strftime("%Y-%m-%d %H:%M:%S"),
        "amount": amount,
        "declared_instrument": declared_inst,
        "sub_instrument": sub_inst,
        "card_bin": card_bin,
        "card_tier": card_tier,
        "mcc": mcc,
        "merchant_true_category": merchant_category,
        "tax_amount_provided": tax_amount_provided,
        "po_code_provided": po_code_provided,
        "line_item_detail_provided": line_item_provided,
        "contracted_flat_rate": contracted_flat_rate,
        "fee_charged": fee_charged,
        "tax_charged": tax_charged,
        "turnover_tier": turnover_tier,
        "injected_issue": injected_issue,
    }


def generate_dataset(
    config: Optional[Dict[str, Any]] = None,
    msa: Optional[Dict[str, Any]] = None
) -> pd.DataFrame:
    """Generates a synthetic settlement transactions DataFrame based on config.
    
    Config parameters:
    - num_transactions (int, default 500)
    - min_amount (float, default 50.0)
    - max_amount (float, default 100000.0)
    - rupay_credit_leak_rate (float, default 0.15)
    - l2_l3_downgrade_rate (float, default 0.12)
    - mcc_misclass_rate (float, default 0.10)
    - exception_rate (float, default 0.05)
    """
    cfg = config or {}
    row_count = int(cfg.get("num_transactions", 500))

    # Support amount_range tuple/list or min/max keys
    if "amount_range" in cfg and isinstance(cfg["amount_range"], (list, tuple)) and len(cfg["amount_range"]) == 2:
        min_amount = float(cfg["amount_range"][0])
        max_amount = float(cfg["amount_range"][1])
    else:
        min_amount = float(cfg.get("min_amount", 50.0))
        max_amount = float(cfg.get("max_amount", 100000.0))

    rates = {
        "rupay_credit_leak_rate": float(cfg.get("rupay_credit_leak_rate", 0.15)),
        "l2_l3_downgrade_rate": float(cfg.get("l2_l3_downgrade_rate", 0.12)),
        "mcc_misclass_rate": float(cfg.get("mcc_misclass_rate", 0.10)),
        "exception_rate": float(cfg.get("exception_rate", 0.05)),
    }

    # Resolve active MSA
    active_msa = msa
    if active_msa is None:
        msa_path = Path("data/raw/merchant_msa.json")
        if msa_path.exists():
            with open(msa_path, "r", encoding="utf-8") as f:
                active_msa = json.load(f)
        else:
            active_msa = generate_msa()

    start_date = datetime(2026, 8, 15, 9, 0, 0)
    records = [
        generate_transaction(
            tx_id=i + 1,
            start_date=start_date,
            msa=active_msa,
            min_amount=min_amount,
            max_amount=max_amount,
            rates=rates,
        )
        for i in range(row_count)
    ]

    return pd.DataFrame(records)


def generate_batch(row_count: int = 500) -> None:
    """CLI helper to generate default batch and write to data/raw/settlement_batch_01.csv."""
    random.seed(42)
    output_dir = Path("data/raw")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    df = generate_dataset({"num_transactions": row_count})
    output_path = output_dir / "settlement_batch_01.csv"
    df.to_csv(output_path, index=False)

    print(f"[InterDrift] Successfully generated {len(df)} records at: {output_path}")
    print("\n--- Injected Issues Breakdown ---")
    print(df["injected_issue"].value_counts())


if __name__ == "__main__":
    generate_batch(500)
