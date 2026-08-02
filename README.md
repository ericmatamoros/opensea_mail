# NFT and token price alerts

This project checks configured OpenSea collection floor prices and CoinMarketCap token
prices, then sends email through Gmail SMTP.

The GitHub Actions workflow runs at **05:00 UTC every Monday, Wednesday, and Saturday**:

- Monday and Wednesday send an email only when a price is below or above its configured
  thresholds.
- Saturday sends one complete report containing every configured NFT and token price,
  including assets currently within range.
- The entire Actions job is stopped after five minutes. Individual HTTP and SMTP calls
  also have short timeouts so network issues fail cleanly.
- If setup, tests, price collection, or email delivery fails—or the five-minute limit is
  exceeded—a separate job sends a failure email with a link to the Actions run.

The workflow can also be started manually from GitHub. Select the `report` input to send
the complete report; otherwise the manual run uses alert-only behavior.

## Configuration

Alert thresholds and display names live in
`opensea_mail/config/config.yaml`. Each item needs a lower threshold strictly below its
upper threshold.

The following secrets are required locally in `opensea_mail/.env` and in the repository's
GitHub Actions secrets:

```dotenv
OPENSEA_KEY=
COINMARKETCAP_KEY=
SENDER_EMAIL=
RECEIVER_EMAIL=
SENDER_PASSWORD=
```

`SENDER_PASSWORD` should be a Gmail app password, not the account password. The `.env`
file is ignored by Git and must never be committed.

## Local setup and checks

```bash
python3 -m venv .venv
source .venv/bin/activate
make install
make test
make dry-run
```

`make dry-run` contacts both live APIs and renders the Saturday report in the terminal,
but does not send email. Use `make run` for alert-only delivery or `make report` for a
complete delivered report.
