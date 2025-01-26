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
from imei_services.imeicheck_net import ImeiChecker

log = get_logger(__name__)  # get configured logger

load_dotenv()
bot = telebot.TeleBot(os.getenv("TG_TOKEN"), parse_mode="Markdown")
imei_checker = ImeiChecker(os.getenv("IMEICHECK_NET_TOKEN"))
print(f"Current token: {os.getenv("IMEICHECK_NET_TOKEN")}")


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


@bot.message_handler(commands=["check_imei"])
def check_imei(message: Message):
    if message.text == "/check_imei":
        services = imei_checker.get_services()
        services.sort(key=lambda service: service["id"])
        text_rows = "\n".join(
            [
                f"{str(s['id']).ljust(2)} {s['price']} {s['title']}"
                for s in services
            ]
        )

        text = "Send a command like:\n/check\\_imei 123456789012345 *id*\n"
        text += "Where instead of id will be the id of the service you need from the table below:"
        text += f"\n```id|price|title\n{text_rows}```"
        bot.send_message(
            chat_id=message.chat.id,
            text=text,
        )
        return

    try:
        log.info(f"User {message.chat.id} launched IMEI check.")

        _, imei, service_id = message.text.split()
        imei_data = imei_checker.get_imei_info(
            imei=imei,
            service_id=int(service_id),
        )
        text = "\n".join([f"{k}: {v}" for k, v in imei_data.items()])

    except ValueError:
        log.error(f"Invalid command format, user: {message.chat.id}")
        text = "Invalid command format, correct example:\n/check_imei 123456789012345 1"

    except Exception as e:
        log.error(f"Error while checking IMEI: {e}")
        text = f"An error occurred: {str(e)}"

    bot.reply_to(
        message=message,
        text=text,
        parse_mode="html",
    )


@bot.message_handler(commands=["balance"])
def check_balance(message: Message):
    balance = imei_checker.get_balance()
    service_name = imei_checker.get_service_name()
    bot.send_message(
        chat_id=message.chat.id,
        text=f"Service: *{service_name}*\nAccount balance: *{balance}*"
    )


@bot.message_handler(func=lambda message: True)
def handle_all_messages(message: Message):
    bot.reply_to(message=message, text="Unsupported command.")


if __name__ == "__main__":
    init_db()
    log.info("The bot is running...")
    bot.polling(non_stop=True)
