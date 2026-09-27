#!/usr/bin/env python3
"""Offline, credential-free tests for the Claude free-model cost gate."""
import unittest
from decimal import Decimal

from claude_free_preflight import validate_model

MODEL = "nvidia/nemotron-3-super-120b-a12b:free"


def catalog_item(pricing=None, tools=True):
    return {
        "id": MODEL,
        "pricing": pricing if pricing is not None else {"prompt": "0", "completion": "0"},
        "supported_parameters": ["tools", "tool_choice"] if tools else ["temperature"],
    }


class FreeModelTests(unittest.TestCase):
    def test_valid_free_model(self):
        self.assertEqual(validate_model(MODEL, [catalog_item()])["id"], MODEL)

    def test_rejects_paid_selection(self):
        with self.assertRaisesRegex(ValueError, "explicit"):
            validate_model("anthropic/claude-sonnet-latest", [catalog_item()])

    def test_rejects_nonzero_price(self):
        with self.assertRaisesRegex(ValueError, "not zero"):
            validate_model(MODEL, [catalog_item({"prompt": "0.001", "completion": "0"})])

    def test_rejects_missing_model(self):
        with self.assertRaisesRegex(ValueError, "absent"):
            validate_model(MODEL, [])

    def test_rejects_missing_tool_support(self):
        with self.assertRaisesRegex(ValueError, "tool support"):
            validate_model(MODEL, [catalog_item(tools=False)])

    def test_rejects_missing_prices(self):
        with self.assertRaisesRegex(ValueError, "Missing"):
            validate_model(MODEL, [catalog_item({"prompt": "0"})])

    def test_rejects_nan_price(self):
        with self.assertRaisesRegex(ValueError, "not zero"):
            validate_model(MODEL, [catalog_item({"prompt": "NaN", "completion": "0"})])

    def test_decimal_comparison_is_exact(self):
        self.assertEqual(Decimal("0"), Decimal("0.0"))


if __name__ == "__main__":
    unittest.main()
