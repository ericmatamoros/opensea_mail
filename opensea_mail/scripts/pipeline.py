import os
from datetime import datetime
from dotenv import load_dotenv
import yaml

from opensea_mail import CONFIG_PATH, logger
from opensea_mail.interfaces import (
    CoinMarketCapCollector,
    OpenSeaCollector, 
    MailSender
)


load_dotenv()
def main() -> None:
    with open(CONFIG_PATH / "config.yaml") as file:
        settings = yaml.load(file, Loader=yaml.FullLoader)

    if 'nft_collections' in settings.keys():
        # Evaluate for NFT
        _evaluate_price(settings['nft_collections'], 'FP', settings['send_analytics'])

    if 'crypto_currency' in settings.keys():
        # Evaluate for Crypto
        _evaluate_price(settings['crypto_currency'], 'PRICE', settings['send_analytics'])


def _evaluate_price(elements: dict, str_eval: str,  send_analytic: bool ) -> None:
    """Evaluate price of an NFT collection or a Cryptocurrency.
    
    Evaluation is done through lower bounds & upper bounds set by user in the configuration file, and
    it will report if the currency/collection undegoes or surpasses the thresholds.
    
    :param elements: Dictionary with element and lower/upper bounds.
    :param str_eval: Either wants to evaluate the 'PRICE' or the 'NFT'.
    :param send_analytic: If True, send email in case that price is outside the user-specified bounds.
      """

    for element, thresholds in elements.items():
            lower_thr = min(thresholds)
            upper_thr = max(thresholds)
            logger.info(f"Lower threshold {str_eval} for {element}: {lower_thr}")
            logger.info(f"Upper threshold {str_eval} for {element}: {upper_thr}")

            if str_eval == 'FP':
                logger.info(f"Scrapping data for collection: {element}")
                scrapper = OpenSeaCollector(api_key = os.getenv("OPENSEA_KEY", ""), collection = element)
                current_val = scrapper.get_fp()
            elif str_eval == 'PRICE':
                scrapper = CoinMarketCapCollector(api_key = os.getenv("COINMARKETCAP_KEY", ""), ticker = element)
                current_val = scrapper.get_price()
            else:
                raise Exception("Not a supported scrapper method used. Only accepted 'FP' or 'PRICE'")

                
            logger.info(f"Current {str_eval} of {element.upper()} is:  {current_val}")
            if (current_val != -1):

                if (current_val > upper_thr):
                    subject = f"{str_eval} ABOVE THRESHOLD ON {element.upper()}"
                    body= f"Current {str_eval} of {element.upper()} is: {current_val}, which is above the threshold {str_eval} of {upper_thr}"
                elif (current_val < lower_thr):
                    subject = f"{str_eval} BELOW THRESHOLD ON {element.upper()}"
                    body= f"Current {str_eval} of {element.upper()} is: {current_val}, which is below the threshold {str_eval} of {lower_thr}"
                else:
                    send_analytic = False

                
                # Send analytics via mail
                if send_analytic:
                    sender = MailSender(
                        subject=subject,
                        body= body,
                        sender_email=os.getenv("SENDER_EMAIL", ""),
                        receiver_email=os.getenv("RECEIVER_EMAIL", ""),
                        password=os.getenv("SENDER_PASSWORD", "")
                    )
                    sender.send_email()

            else:
                logger.warn("Floor price of collection could not be fetched.")

            logger.info("###################################")


if __name__ == "__main__":
    main()
