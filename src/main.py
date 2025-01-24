import os

from dotenv import load_dotenv
import telebot
from telebot.types import Message

from logger_config import get_logger
from database import (
    init_db,
    create_user,
    is_user_admin,
    update_user,
)

log = get_logger(__name__)  # get configured logger

load_dotenv()
bot = telebot.TeleBot(os.getenv("TG_TOKEN"), parse_mode="Markdown")


@bot.message_handler(commands=["start"])
def send_welcome(message):
    bot.send_message(
        chat_id=message.chat.id,
        text="You started the bot!\n/help for available commands",
    )


@bot.message_handler(commands=["help"])
def send_help(message):
    help_text = "Вот список доступных комманд:\n"
    commands = bot.get_my_commands()
    for command in commands:
        help_text += f"/{command.command} - {command.description}\n"
    bot.send_message(
        chat_id=message.chat.id,
        text=help_text,
    )


@bot.message_handler(commands=["add_user"])
def add_user(message: Message):
    is_admin = is_user_admin(tg_id=message.chat.id)
    if is_admin:
        try:
            _, tg_id, name = message.text.split()
            tg_id = int(tg_id)
            print(f"{name=}, {tg_id=}")

            user_created = create_user(tg_id=tg_id, name=name)
            if user_created:
                text = f"User with id *{tg_id}* registered."
            else:
                text = "An error occurred during user registration."

        except ValueError:
            text = "Invalid command format, correct example:\n/add 1234567890 John"
    else:
        text = "You do not have permission for this command. Admins only."

    bot.send_message(
        chat_id=message.chat.id,
        text=text,
    )


@bot.message_handler(commands=["change_role"])
def change_user_role(message: Message):
    is_admin = is_user_admin(tg_id=message.chat.id)
    if is_admin:
        try:
            _, tg_id, role = message.text.split()
            tg_id = int(tg_id)

            if tg_id == message.chat.id:
                bot.send_message(
                    chat_id=message.chat.id,
                    text="You can't change your role.",
                )
                return

            if update_user(tg_id=tg_id, new_role=role):
                text = f"User *{tg_id}* has new role: *{role}*."
            else:
                text = "User was not found or role is invalid."

        except ValueError:
            text = "Invalid command format, correct example:\n/change\\_role 1234567890 admin"

    else:
        text = "You do not have permission for this command. Admins only."

    bot.send_message(
        chat_id=message.chat.id,
        text=text,
    )


@bot.message_handler(commands=["change_status"])
def change_user_status(message: Message):
    is_admin = is_user_admin(tg_id=message.chat.id)
    if is_admin:
        try:
            _, tg_id, status = message.text.split()
            tg_id = int(tg_id)
            if tg_id == message.chat.id:
                bot.send_message(
                    chat_id=message.chat.id,
                    text="You can't change your status.",
                )
                return

            if update_user(tg_id=tg_id, new_status=status):
                text = f"User *{tg_id}* is *{status}* now."
            else:
                text = "User was not found or status is invalid."

        except ValueError:
            text = "Invalid command format, correct example:\n/change\\_status 1234567890 disabled"

    else:
        text = "You do not have permission for this command. Admins only."

    bot.send_message(
        chat_id=message.chat.id,
        text=text,
    )


@bot.message_handler(func=lambda message: True)
def handle_all_messages(message: Message):
    bot.reply_to(message=message, text="Unsupported command.")


if __name__ == "__main__":
    init_db()
    log.info("The bot is running...")
    bot.polling(non_stop=True)
