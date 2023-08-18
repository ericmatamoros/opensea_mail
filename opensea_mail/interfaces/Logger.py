import logging

from opensea_mail import DATA_PATH


class Logger:
    def __init__(self, filename: str) -> None:
        self._filename = filename

    def write_logs(self):
        _clear_log_file(DATA_PATH / self._filename)

        # Clear existing handlers from the root logger
        root_logger = logging.getLogger()
        for handler in root_logger.handlers:
            root_logger.removeHandler(handler)

        # Configure the logger
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(levelname)s - %(message)s",
            handlers=[logging.FileHandler(DATA_PATH / self._filename), logging.StreamHandler()],
        )


def _clear_log_file(log_file_path: str):
    with open(log_file_path, "w") as log_file:
        log_file.truncate()  # Truncate the file using the truncate method
