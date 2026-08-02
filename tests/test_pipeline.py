import tempfile
import unittest
from pathlib import Path

from opensea_mail.scripts.pipeline import Asset, PriceResult, build_message, load_assets


class PriceResultTests(unittest.TestCase):
    def setUp(self) -> None:
        self.asset = Asset("ETH", "Ethereum", "token", "USD", 1200.0, 2000.0)

    def test_threshold_boundaries_are_within_range(self) -> None:
        self.assertEqual(PriceResult(self.asset, 1200.0).status, "within")
        self.assertEqual(PriceResult(self.asset, 2000.0).status, "within")

    def test_values_outside_thresholds_alert(self) -> None:
        self.assertEqual(PriceResult(self.asset, 1199.0).status, "below")
        self.assertEqual(PriceResult(self.asset, 2001.0).status, "above")


class MessageTests(unittest.TestCase):
    def setUp(self) -> None:
        self.asset = Asset("ETH", "Ethereum", "token", "USD", 1200.0, 2000.0)

    def test_alert_mode_omits_in_range_prices(self) -> None:
        message = build_message([PriceResult(self.asset, 1500.0)], [], report=False)
        self.assertIsNone(message)

    def test_report_mode_includes_in_range_prices(self) -> None:
        subject, body = build_message(
            [PriceResult(self.asset, 1500.0)], [], report=True
        )
        self.assertIn("Weekly", subject)
        self.assertIn("Ethereum: 1,500.00 USD", body)
        self.assertIn("within", body)

    def test_alert_mode_includes_only_breaches(self) -> None:
        other = Asset("NFT", "Example NFT", "NFT", "ETH", 7.5, 9.2)
        subject, body = build_message(
            [PriceResult(self.asset, 2100.0), PriceResult(other, 8.0)],
            [],
            report=False,
        )
        self.assertIn("1 asset outside", subject)
        self.assertIn("Ethereum", body)
        self.assertNotIn("Example NFT", body)


class ConfigurationTests(unittest.TestCase):
    def _load(self, text: str):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "config.yaml"
            path.write_text(text, encoding="utf-8")
            return load_assets(path)

    def test_structured_configuration_loads(self) -> None:
        assets, enabled = self._load(
            """
nft_collections:
  boredapeyachtclub:
    name: Bored Ape Yacht Club
    lower: 7.5
    upper: 9.2
crypto_currency:
  ETH:
    name: Ethereum
    lower: 1200
    upper: 2000
send_email: true
"""
        )
        self.assertEqual(
            [asset.identifier for asset in assets], ["boredapeyachtclub", "ETH"]
        )
        self.assertTrue(enabled)

    def test_invalid_range_is_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "lower must be less"):
            self._load(
                """
crypto_currency:
  ETH:
    lower: 2000
    upper: 1200
"""
            )


if __name__ == "__main__":
    unittest.main()
