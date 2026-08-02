import unittest
from unittest.mock import MagicMock, patch

import requests

from opensea_mail.interfaces import CoinMarketCapCollector, MailSender, OpenSeaCollector


class OpenSeaCollectorTests(unittest.TestCase):
    @patch("opensea_mail.interfaces.open_sea_collector.requests.get")
    def test_parses_floor_price_and_sets_timeout(self, get: MagicMock) -> None:
        response = get.return_value
        response.json.return_value = {"total": {"floor_price": 8.3}}

        value = OpenSeaCollector("key", "boredapeyachtclub").get_fp()

        self.assertEqual(value, 8.3)
        response.raise_for_status.assert_called_once_with()
        self.assertEqual(get.call_args.kwargs["timeout"], 20.0)

    @patch("opensea_mail.interfaces.open_sea_collector.requests.get")
    def test_wraps_network_errors(self, get: MagicMock) -> None:
        get.side_effect = requests.Timeout("timed out")
        with self.assertRaisesRegex(RuntimeError, "Could not fetch"):
            OpenSeaCollector("key", "boredapeyachtclub").get_fp()


class CoinMarketCapCollectorTests(unittest.TestCase):
    @patch("opensea_mail.interfaces.coin_market_cap_collector.requests.get")
    def test_parses_usd_price_and_normalizes_ticker(self, get: MagicMock) -> None:
        response = get.return_value
        response.json.return_value = {
            "data": {"ETH": {"quote": {"USD": {"price": 1865.02}}}}
        }

        value = CoinMarketCapCollector("key", "eth").get_price()

        self.assertEqual(value, 1865.02)
        response.raise_for_status.assert_called_once_with()
        self.assertEqual(get.call_args.kwargs["params"]["symbol"], "ETH")
        self.assertEqual(get.call_args.kwargs["timeout"], 20.0)


class MailSenderTests(unittest.TestCase):
    @patch("opensea_mail.interfaces.mail_sender.smtplib.SMTP")
    def test_sends_with_bounded_smtp_connection(self, smtp: MagicMock) -> None:
        sender = MailSender(
            "Subject", "Body", "from@example.com", "to@example.com", "pw"
        )
        sender.send_email()

        smtp.assert_called_once_with("smtp.gmail.com", 587, timeout=30.0)
        server = smtp.return_value.__enter__.return_value
        server.starttls.assert_called_once_with()
        server.login.assert_called_once_with("from@example.com", "pw")
        server.send_message.assert_called_once()

    def test_rejects_missing_credentials(self) -> None:
        with self.assertRaisesRegex(ValueError, "SENDER_PASSWORD"):
            MailSender("Subject", "Body", "from@example.com", "to@example.com", "")


if __name__ == "__main__":
    unittest.main()
