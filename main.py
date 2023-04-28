from dotenv import dotenv_values

from classes.telegrambot import TelegramBot

if __name__ == '__main__':
    ENV_CONFIG = dotenv_values()
    telegram_bot = TelegramBot(ENV_CONFIG)
    telegram_bot.start()
