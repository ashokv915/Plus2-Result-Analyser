import logging
from logging.handlers import RotatingFileHandler

LOG_FILE = "./logs/app.log"

logging.basicConfig(
    filename=LOG_FILE,
    encoding="utf-8",
    filemode="a",
    format="{asctime} - {levelname} - {message}",
    style="{",
    datefmt="%Y-%m-%d %H:%M",
    level=logging.DEBUG,
)

handler = RotatingFileHandler(LOG_FILE, maxBytes=5*1024*1024, backupCount=3)


logging.warning("This is a warning...")