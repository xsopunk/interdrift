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