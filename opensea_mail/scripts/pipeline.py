from datetime import datetime
import yaml

from opensea_mail import CONFIG_PATH, logger
from opensea_mail.interfaces import OpenSeaCollector, MailSender

def main() -> None:
    with open(CONFIG_PATH / "config.yaml") as file:
        settings = yaml.load(file, Loader=yaml.FullLoader)

    for collection, fp_threshold in settings['nft_collections'].items():
        logger.info(f"Scrapping data for collection: {collection}")
        scrapper = OpenSeaCollector(api_key = settings['opensea_key'], collection = collection)

        current_fp = scrapper.get_fp()
        logger.info(f"Current Floor Price of collection is:  {current_fp}")
        if (current_fp > fp_threshold) & (current_fp != -1):
            # Send analytics via mail
            if settings["send_analytics"]:
                sender = MailSender(
                    subject=f"FP of {fp_threshold} surpassed on {collection.upper()}",
                    body= f"Current FP of {collection.upper()} is: {current_fp}, which is lower than threshold FP of {fp_threshold}",
                    sender_email=settings["sender_mail"],
                    receiver_email=settings["receiver_mail"],
                    password=settings["sender_password"],
                )
                sender.send_email()

        elif (current_fp == -1):
            logger.warn("Floor price of collection could not be fetched.")
        else:
            logger.info(f"Floor price is {current_fp} which is lower than threshold of {fp_threshold}")

        logger.info("###################################")


if __name__ == "__main__":
    main()
