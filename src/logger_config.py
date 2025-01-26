import logging

logging.basicConfig(
    level=logging.INFO,  # minimal logging level

    # message format
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[
        logging.StreamHandler(),  # console output
        logging.FileHandler("../logs/app.log"),  # file output
    ],
)


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)
