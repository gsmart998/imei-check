import os

from dotenv import load_dotenv
import telebot
from telebot.types import BotCommand

from logger_config import get_logger


log = get_logger(__name__)  # get configured logger

load_dotenv()
bot = telebot.TeleBot(os.getenv("TG_TOKEN"), parse_mode="Markdown")

bot_commands = [
    BotCommand("start", "Start this bot."),
    BotCommand("check_imei", "Command to check IMEI."),
    BotCommand("balance", "Command to check account balance in the service."),
    BotCommand("add_user", "Command to add a new user (admin only)."),
    BotCommand("change_role", "Command to change user role (admin only)."),
    BotCommand("change_status", "Command to change user status (admin only)."),
    BotCommand("help", "List of available commands."),
]
