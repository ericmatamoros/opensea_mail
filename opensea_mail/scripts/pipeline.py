import os
from datetime import datetime
from dotenv import load_dotenv
import yaml

from opensea_mail import CONFIG_PATH, logger
from opensea_mail.interfaces import OpenSeaCollector, MailSender


load_dotenv()

def main() -> None:
    with open(CONFIG_PATH / "config.yaml") as file:
        settings = yaml.load(file, Loader=yaml.FullLoader)

    for collection, fps in settings['nft_collections'].items():
        fp_lower_thr = min(fps)
        fp_upper_thr = max(fps)
        logger.info(f"Lower threshold FP for {collection}: {fp_lower_thr}")
        logger.info(f"Upper threshold FP for {collection}: {fp_upper_thr}")

        logger.info(f"Scrapping data for collection: {collection}")
        scrapper = OpenSeaCollector(api_key = os.getenv("OPENSEA_KEY", ""), collection = collection)

        current_fp = scrapper.get_fp()
        logger.info(f"Current Floor Price of collection is:  {current_fp}")
        if (current_fp != -1):

            if (current_fp > fp_upper_thr):
                subject = f"FP ABOVE THRESHOLD ON {collection.upper()}"
                body= f"Current FP of {collection.upper()} is: {current_fp}, which is above the threshold FP of {fp_upper_thr}"
                send_analytic = settings["send_analytics"]
            elif (current_fp < fp_lower_thr):
                subject = f"FP BELOW THRESHOLD ON {collection.upper()}"
                body= f"Current FP of {collection.upper()} is: {current_fp}, which is below the threshold FP of {fp_lower_thr}"
                send_analytic = settings["send_analytics"]
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
