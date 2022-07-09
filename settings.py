# built-in
import logging
# external
import telebot
# project
import config


__all__ = ['logger', 'bot']


# LOGGER

handler = logging.FileHandler("log.log")
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s - %(lineno)d'
)

logger = logging.getLogger('default')
logger.setLevel(logging.INFO)

handler.setFormatter(formatter)
logger.addHandler(handler)

# TELEGRAM

bot = telebot.TeleBot(config.TOKEN)
