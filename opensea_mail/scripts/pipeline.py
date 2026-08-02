"""Collect configured prices and send threshold alerts or a weekly report."""

from __future__ import annotations

import argparse
import os
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml
from dotenv import load_dotenv

from opensea_mail import BASE_PATH, CONFIG_PATH, logger
from opensea_mail.interfaces import CoinMarketCapCollector, MailSender, OpenSeaCollector


@dataclass(frozen=True)
class Asset:
    identifier: str
    name: str
    asset_type: str
    unit: str
    lower: float
    upper: float


@dataclass(frozen=True)
class PriceResult:
    asset: Asset
    value: float

    @property
    def status(self) -> str:
        if self.value < self.asset.lower:
            return "below"
        if self.value > self.asset.upper:
            return "above"
        return "within"

    @property
    def is_alert(self) -> bool:
        return self.status != "within"


def _parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--report",
        action="store_true",
        help="Send a complete report, including prices within their configured ranges.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Fetch live prices and render the email without sending it.",
    )
    parser.add_argument(
        "--config",
        type=Path,
        default=CONFIG_PATH / "config.yaml",
        help="Path to the YAML configuration file.",
    )
    return parser.parse_args(argv)


def _number(value: Any, field: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise TypeError(f"{field} must be a number")
    return float(value)


def _asset_from_config(identifier: str, raw: Any, asset_type: str, unit: str) -> Asset:
    if isinstance(raw, Mapping):
        name = str(raw.get("name", identifier))
        lower = _number(raw.get("lower"), f"{identifier}.lower")
        upper = _number(raw.get("upper"), f"{identifier}.upper")
    elif (
        isinstance(raw, Sequence)
        and not isinstance(raw, (str, bytes))
        and len(raw) == 2
    ):
        name = identifier
        lower = _number(raw[0], f"{identifier}[0]")
        upper = _number(raw[1], f"{identifier}[1]")
    else:
        raise TypeError(
            f"{identifier} must define name/lower/upper or contain [lower, upper]"
        )

    if lower >= upper:
        raise ValueError(f"{identifier}.lower must be less than {identifier}.upper")

    return Asset(identifier, name, asset_type, unit, lower, upper)


def load_assets(config_path: Path) -> tuple[list[Asset], bool]:
    """Load and validate all tracked assets and the email toggle."""
    try:
        with config_path.open(encoding="utf-8") as config_file:
            settings = yaml.safe_load(config_file) or {}
    except (OSError, yaml.YAMLError) as exc:
        raise ValueError(f"Could not load configuration {config_path}: {exc}") from exc

    if not isinstance(settings, Mapping):
        raise TypeError("The configuration root must be a mapping")

    assets: list[Asset] = []
    sections = (
        ("nft_collections", "NFT", "ETH"),
        ("crypto_currency", "token", "USD"),
    )
    for section, asset_type, unit in sections:
        entries = settings.get(section, {})
        if not isinstance(entries, Mapping):
            raise TypeError(f"{section} must be a mapping")
        assets.extend(
            _asset_from_config(str(identifier), raw, asset_type, unit)
            for identifier, raw in entries.items()
        )

    if not assets:
        raise ValueError(
            "At least one NFT collection or cryptocurrency must be configured"
        )

    # Keep accepting the old key so existing private configurations do not break.
    send_email = settings.get("send_email", settings.get("send_analytics", True))
    if not isinstance(send_email, bool):
        raise TypeError("send_email must be true or false")
    return assets, send_email


def collect_prices(assets: Iterable[Asset]) -> tuple[list[PriceResult], list[str]]:
    """Fetch every asset, continuing so one failed API does not hide other results."""
    results: list[PriceResult] = []
    errors: list[str] = []

    for asset in assets:
        logger.info("Fetching %s price for %s", asset.asset_type, asset.name)
        try:
            if asset.asset_type == "NFT":
                value = OpenSeaCollector(
                    api_key=os.getenv("OPENSEA_KEY", ""),
                    collection=asset.identifier,
                ).get_fp()
            else:
                value = CoinMarketCapCollector(
                    api_key=os.getenv("COINMARKETCAP_KEY", ""),
                    ticker=asset.identifier,
                ).get_price()
        except (RuntimeError, ValueError) as exc:
            message = f"{asset.name}: {exc}"
            logger.error(message)
            errors.append(message)
            continue

        result = PriceResult(asset=asset, value=value)
        results.append(result)
        logger.info(
            "%s: %s %s (%s configured range)",
            asset.name,
            _format_number(value),
            asset.unit,
            result.status,
        )

    return results, errors


def _format_number(value: float) -> str:
    if value >= 100:
        return f"{value:,.2f}"
    if value >= 1:
        return f"{value:,.4f}".rstrip("0").rstrip(".")
    return f"{value:,.8f}".rstrip("0").rstrip(".")


def _result_line(result: PriceResult) -> str:
    asset = result.asset
    value = _format_number(result.value)
    lower = _format_number(asset.lower)
    upper = _format_number(asset.upper)
    return (
        f"- {asset.asset_type} — {asset.name}: {value} {asset.unit} "
        f"[{result.status}; alert range: below {lower} or above {upper} {asset.unit}]"
    )


def build_message(
    results: Sequence[PriceResult], errors: Sequence[str], report: bool
) -> tuple[str, str] | None:
    selected = (
        list(results) if report else [result for result in results if result.is_alert]
    )
    if not selected and not (report and errors):
        return None

    if report:
        subject = "Weekly NFT and token price report"
        intro = "Current prices for all configured alerts:"
    else:
        count = len(selected)
        subject = f"Price alert: {count} asset{'s' if count != 1 else ''} outside range"
        intro = "The following configured price thresholds were crossed:"

    lines = [intro, "", *(_result_line(result) for result in selected)]
    if errors:
        lines.extend(["", "Unavailable prices:", *(f"- {error}" for error in errors)])
    return subject, "\n".join(lines)


def main(argv: Sequence[str] | None = None) -> int:
    args = _parse_args(argv)
    load_dotenv(BASE_PATH / ".env")

    try:
        assets, email_enabled = load_assets(args.config)
    except (TypeError, ValueError) as exc:
        logger.error(str(exc))
        return 2

    results, errors = collect_prices(assets)
    message = build_message(results, errors, report=args.report)

    if message is None:
        logger.info("All prices are within range; no alert email is needed.")
    elif not email_enabled:
        logger.info("Email delivery is disabled by configuration.")
    elif args.dry_run:
        logger.info("Dry run; email was not sent.\nSubject: %s\n\n%s", *message)
    else:
        try:
            MailSender(
                subject=message[0],
                body=message[1],
                sender_email=os.getenv("SENDER_EMAIL", ""),
                receiver_email=os.getenv("RECEIVER_EMAIL", ""),
                password=os.getenv("SENDER_PASSWORD", ""),
            ).send_email()
            logger.info("Email sent successfully.")
        except (OSError, RuntimeError, ValueError) as exc:
            logger.error("Could not send email: %s", exc)
            return 1

    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
