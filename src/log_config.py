import logging

logging.basicConfig(
    filename="black76_api.log",
    level=logging.INFO,
    format="%(asctime)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

LOGGER = logging.getLogger("black76_api_logger")
