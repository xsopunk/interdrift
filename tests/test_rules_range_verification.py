"""
Unit tests for Step 2: Verification of ₹1,00,000 amount-range widening
against turnover-tier dependent rules (R7/R8) and all range-dependent rule logic.
"""

import unittest
import pandas as pd
from src.rules_engine.rule_loader import load_rules
from src.rules_engine.row_classifier import classify_row, compute_expected_fee
from src.data_generation.generate_settlement_data import (
    generate_dataset,
    generate_msa,
    calculate_expected_fee,
)


class TestRulesRangeWidening(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.rules = load_rules()
        cls.rules_dict = {r["rule_id"]: r for r in cls.rules}

    def test_r7_small_merchant_debit_cap_at_100k(self):
        """R7: Visa/Mastercard debit for small merchants (<=20L) capped at 0.40% or max Rs 200."""
        r7 = self.rules_dict["R7"]
        # At Rs 100,000, 0.40% = Rs 400, so it must cap at Rs 200.00
        row = pd.Series({
            "transaction_id": "TEST_R7_01",
            "amount": 100000.0,
            "declared_instrument": "Card",
            "sub_instrument": "Debit_non_rupay",
            "turnover_tier": "below_20L",
            "fee_charged": 200.0,
        })
        expected = compute_expected_fee(row, r7)
        self.assertEqual(expected, 200.0)

        # In generator logic:
        gen_fee = calculate_expected_fee("Debit_non_rupay", 100000.0, "below_20L", "5045")
        self.assertEqual(gen_fee, 200.0)

        # Full classification check:
        res = classify_row(row, self.rules)
        self.assertEqual(res["classification"], "Matched")
        self.assertEqual(res["matched_rule_id"], "R7")
        self.assertEqual(res["expected_fee"], 200.0)

    def test_r8_large_merchant_debit_cap_at_100k_and_above(self):
        """R8: Visa/Mastercard debit for large merchants (>20L) capped at 0.90% or max Rs 1,000."""
        r8 = self.rules_dict["R8"]
        # At Rs 100,000, 0.90% = Rs 900, which is below the Rs 1,000 cap
        row_100k = pd.Series({
            "transaction_id": "TEST_R8_100K",
            "amount": 100000.0,
            "declared_instrument": "Card",
            "sub_instrument": "Debit_non_rupay",
            "turnover_tier": "above_20L",
            "fee_charged": 900.0,
        })
        expected_100k = compute_expected_fee(row_100k, r8)
        self.assertEqual(expected_100k, 900.0)

        gen_fee_100k = calculate_expected_fee("Debit_non_rupay", 100000.0, "above_20L", "5045")
        self.assertEqual(gen_fee_100k, 900.0)

        res_100k = classify_row(row_100k, self.rules)
        self.assertEqual(res_100k["classification"], "Matched")
        self.assertEqual(res_100k["matched_rule_id"], "R8")

        # At Rs 150,000, 0.90% = Rs 1350, so it must cap at Rs 1,000.00
        row_150k = pd.Series({
            "transaction_id": "TEST_R8_150K",
            "amount": 150000.0,
            "declared_instrument": "Card",
            "sub_instrument": "Debit_non_rupay",
            "turnover_tier": "above_20L",
            "fee_charged": 1000.0,
        })
        expected_150k = compute_expected_fee(row_150k, r8)
        self.assertEqual(expected_150k, 1000.0)

    def test_rupay_credit_upi_at_100k(self):
        """R4: RuPay credit card on UPI transactions over Rs 2,000 incur 1.5% MDR."""
        r4 = self.rules_dict["R4"]
        row = pd.Series({
            "transaction_id": "TEST_R4_100K",
            "amount": 100000.0,
            "declared_instrument": "UPI",
            "sub_instrument": "RuPay_credit_UPI",
            "fee_charged": 1500.0,
        })
        expected = compute_expected_fee(row, r4)
        self.assertEqual(expected, 1500.0)

        res = classify_row(row, self.rules)
        self.assertEqual(res["classification"], "Matched")
        self.assertEqual(res["matched_rule_id"], "R4")

    def test_ppi_wallet_upi_at_100k(self):
        """R6: PPI wallet on UPI over Rs 2,000 with MCC tiering at Rs 100,000."""
        # Education MCC 8220 -> R6a (0.70%)
        row_edu = pd.Series({
            "transaction_id": "TEST_R6A_100K",
            "amount": 100000.0,
            "declared_instrument": "UPI",
            "sub_instrument": "PPI_wallet_UPI",
            "mcc": "8220",
            "fee_charged": 700.0,
        })
        res_edu = classify_row(row_edu, self.rules)
        self.assertEqual(res_edu["classification"], "Matched")
        self.assertEqual(res_edu["matched_rule_id"], "R6a")
        self.assertEqual(res_edu["expected_fee"], 700.0)

        # General Commercial MCC 5045 -> R6c (1.10%)
        row_b2b = pd.Series({
            "transaction_id": "TEST_R6C_100K",
            "amount": 100000.0,
            "declared_instrument": "UPI",
            "sub_instrument": "PPI_wallet_UPI",
            "mcc": "5045",
            "fee_charged": 1100.0,
        })
        res_b2b = classify_row(row_b2b, self.rules)
        self.assertEqual(res_b2b["classification"], "Matched")
        self.assertEqual(res_b2b["matched_rule_id"], "R6c")
        self.assertEqual(res_b2b["expected_fee"], 1100.0)

    def test_full_dataset_generation_and_classification_at_100k_range(self):
        """Generate 500 rows with amount range up to Rs 100,000 and verify classifier stability."""
        msa = generate_msa({"annual_turnover_tier": "below_20L"})
        df = generate_dataset({
            "num_transactions": 500,
            "min_amount": 100.0,
            "max_amount": 100000.0,
        }, msa=msa)

        self.assertEqual(len(df), 500)
        self.assertTrue((df["amount"] >= 100.0).all())
        self.assertTrue((df["amount"] <= 100000.0).all())

        # Run classification on all rows
        results = [classify_row(row, self.rules) for _, row in df.iterrows()]
        classifications = {r["classification"] for r in results}
        self.assertIn("Matched", classifications)
        # Verify no unexpected exceptions or crashes occurred
        for r in results:
            self.assertIn(r["classification"], ["Matched", "Leaked", "Exception", "Flagged_For_Review"])


if __name__ == "__main__":
    unittest.main()
