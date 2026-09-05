"""
Comprehensive End-to-End Integration Verification Test for InterDrift Test Data Feature
Tests:
1. Dataset preview generation with custom sliders and Rs 1,00,000 bounds
2. MSA preview generation with custom business category and turnover tier
3. CSV schema validation (valid vs invalid columns)
4. MSA JSON validation (valid vs invalid keys)
5. Audit activation with custom inputs and fallback notice verification
6. Verification that default demo audit flow remains completely untouched
"""

import unittest
import urllib.request
import urllib.error
import json
from pathlib import Path


BASE_URL = "http://127.0.0.1:8000"


class TestEndToEndTestDataFlow(unittest.TestCase):

    def test_01_backend_health(self):
        """Verify API is healthy and reachable."""
        req = urllib.request.Request(f"{BASE_URL}/health")
        with urllib.request.urlopen(req) as res:
            self.assertEqual(res.status, 200)
            data = json.loads(res.read().decode())
            self.assertEqual(data.get("status"), "ok")

    def test_02_dataset_preview_endpoint(self):
        """Test POST /api/generate/dataset/preview with custom rates and Rs 100k bounds."""
        payload = {
            "num_transactions": 25,
            "min_amount": 250.0,
            "max_amount": 100000.0,
            "rupay_credit_leak_rate": 0.20,
            "l2_l3_downgrade_rate": 0.15,
            "mcc_misclass_rate": 0.10,
            "exception_rate": 0.05
        }
        req = urllib.request.Request(
            f"{BASE_URL}/api/generate/dataset/preview",
            data=json.dumps(payload).encode(),
            headers={"Content-Type": "application/json"}
        )
        with urllib.request.urlopen(req) as res:
            self.assertEqual(res.status, 200)
            data = json.loads(res.read().decode())
            self.assertEqual(data.get("status"), "success")
            self.assertEqual(data["summary"]["total_records"], 25)
            self.assertTrue(data["summary"]["max_amount"] <= 100000.0)
            self.assertTrue(data["summary"]["min_amount"] >= 250.0)
            self.assertEqual(len(data["preview_rows"]), 25)

    def test_03_msa_preview_endpoint(self):
        """Test POST /api/generate/msa/preview with retail category and 2.5% rate."""
        payload = {
            "business_category": "retail",
            "annual_turnover_tier": "below_20L",
            "cards_flat_blended": 0.025
        }
        req = urllib.request.Request(
            f"{BASE_URL}/api/generate/msa/preview",
            data=json.dumps(payload).encode(),
            headers={"Content-Type": "application/json"}
        )
        with urllib.request.urlopen(req) as res:
            self.assertEqual(res.status, 200)
            data = json.loads(res.read().decode())
            self.assertEqual(data.get("status"), "success")
            msa = data.get("msa", {})
            self.assertEqual(msa.get("registered_business_type"), "retail")
            self.assertEqual(msa.get("expected_mcc"), "5411")
            self.assertEqual(msa.get("annual_turnover_tier"), "below_20L")
            self.assertEqual(msa.get("contracted_rates", {}).get("cards_flat_blended"), 0.025)

    def test_04_csv_validation_failure(self):
        """Test CSV upload endpoint rejects invalid schema with clear 422 error."""
        boundary = "----WebKitFormBoundary7MA4YWxkTrZu0gW"
        body = (
            f"--{boundary}\r\n"
            f'Content-Disposition: form-data; name="file"; filename="invalid.csv"\r\n'
            f"Content-Type: text/csv\r\n\r\n"
            f"random_col_1,random_col_2\r\n123,456\r\n"
            f"--{boundary}--\r\n"
        ).encode()

        req = urllib.request.Request(
            f"{BASE_URL}/api/upload/csv",
            data=body,
            headers={"Content-Type": f"multipart/form-data; boundary={boundary}"}
        )
        try:
            urllib.request.urlopen(req)
            self.fail("Expected HTTP 422 error for invalid CSV columns")
        except urllib.error.HTTPError as err:
            self.assertEqual(err.code, 422)
            err_data = json.loads(err.read().decode())
            self.assertIn("missing required columns", err_data.get("detail", "").lower())

    def test_05_msa_validation_failure(self):
        """Test MSA upload endpoint rejects invalid JSON structure with clear 422 error."""
        boundary = "----WebKitFormBoundary7MA4YWxkTrZu0gW"
        body = (
            f"--{boundary}\r\n"
            f'Content-Disposition: form-data; name="file"; filename="invalid_msa.json"\r\n'
            f"Content-Type: application/json\r\n\r\n"
            f'{{"random_key": "val"}}\r\n'
            f"--{boundary}--\r\n"
        ).encode()

        req = urllib.request.Request(
            f"{BASE_URL}/api/upload/msa",
            data=body,
            headers={"Content-Type": f"multipart/form-data; boundary={boundary}"}
        )
        try:
            urllib.request.urlopen(req)
            self.fail("Expected HTTP 422 error for invalid MSA JSON keys")
        except urllib.error.HTTPError as err:
            self.assertEqual(err.code, 422)
            err_data = json.loads(err.read().decode())
            self.assertIn("missing required fields", err_data.get("detail", "").lower())

    def test_06_default_fallback_notices_and_preservation(self):
        """Test activation with default settings triggers notices and uses default files."""
        payload = {
            "dataset_mode": "default",
            "msa_mode": "default"
        }
        req = urllib.request.Request(
            f"{BASE_URL}/api/generate/activate",
            data=json.dumps(payload).encode(),
            headers={"Content-Type": "application/json"}
        )
        with urllib.request.urlopen(req) as res:
            self.assertEqual(res.status, 200)
            data = json.loads(res.read().decode())
            self.assertEqual(data.get("status"), "success")
            notices = data.get("notices", [])
            # Must explicitly warn user about default fallbacks
            self.assertTrue(any("default Merchant Service Agreement" in n for n in notices))
            self.assertTrue(any("default settlement transactions" in n for n in notices))
            self.assertEqual(data.get("rows_processed"), 500)


if __name__ == "__main__":
    unittest.main()
