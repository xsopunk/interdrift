"""
Synthetic Settlement Data Generator
Simulates 500+ Indian merchant payment records with injected fee leakage,
L2/L3 data degradation, and classification exceptions.

"""

import json
import random
from datetime import datetime, timedelta
import pandas as pd
from faker import Faker

fake = Faker("en_IN")
random.seed(42)

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


def generate_transaction(tx_id: int, start_date: datetime, msa: dict) -> dict:
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

    if "UPI" in sub_inst:
        amount = round(random.choice([random.uniform(50, 1500), random.uniform(2050, 7500)]), 2)
        declared_inst = "UPI"
    else:
        amount = round(random.uniform(300, 25000), 2)
        declared_inst = "Card"

    # 2. Metadata & BIN assignment
    card_bin = ""
    card_tier = "N/A"
    if "credit" in sub_inst or "debit" in sub_inst:
        card_bin = random.choice(list(BIN_TIER_MAPPING.keys()))
        _, card_tier = BIN_TIER_MAPPING[card_bin]

    # 3. Establish base fields
    merchant_category = msa["registered_business_type"]
    mcc = msa["expected_mcc"]
    turnover_tier = msa["annual_turnover_tier"]
    contracted_flat_rate = msa["contracted_rates"]["cards_flat_blended"]

    # L2/L3 commercial data fields
    tax_amount_provided = True
    po_code_provided = True
    line_item_provided = True if amount > 10000 else False

    expected_base_fee = calculate_expected_fee(sub_inst, amount, turnover_tier, mcc)
    fee_charged = expected_base_fee
    injected_issue = "clean"

    # 4. Inject intentional anomalies
    roll = random.random()

    # Anomaly A: Zero-MDR Leakage (RuPay credit or PPI over ₹2,000 charged fee when it should be 0%, or vice versa)
    if sub_inst in ["RuPay_credit_UPI", "PPI_wallet_UPI"] and amount <= 2000 and roll < 0.20:
        fee_charged = round(amount * 0.015, 2)  # Charged fee despite zero-fee slab
        injected_issue = "R3_R5_zero_rate_leak"

    # Anomaly B: Non-RuPay Debit cap breach (RBI ₹1,000 cap ignored)
    elif sub_inst == "Debit_non_rupay" and amount > 120000 and roll < 0.40:
        fee_charged = round(amount * 0.009, 2)  # Exceeds ₹1,000 cap
        injected_issue = "R8_debit_cap_breach"

    # Anomaly C: L2/L3 Downgrade on Corporate Cards (R10)
    elif card_tier == "corporate" and roll < 0.35:
        tax_amount_provided = False
        po_code_provided = False
        fee_charged = round(expected_base_fee + (amount * 0.008), 2)  # 80 bps downgrade penalty
        injected_issue = "R10_l2_l3_downgrade"

    # Anomaly D: MCC Misclassification (R12)
    elif roll < 0.10:
        mcc = "5411"  # Force assigned as general grocery instead of B2B wholesale
        injected_issue = "R12_mcc_misclassification"

    # Anomaly E: Sub-instrument missing (Unclassifiable Exception)
    elif roll < 0.06:
        sub_inst = ""  # Left blank to simulate missing tag from raw aggregator feed
        injected_issue = "exception_missing_tag"

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