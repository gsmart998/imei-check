import os

from dotenv import load_dotenv
from telebot.types import Message

from imei_services.imeicheck_net import ImeiCheckClient
from bot import bot, bot_commands
from logger_config import get_logger
from database.database import (
    create_user,
    update_user,
    check_user_permissions,
    init_db,
)

log = get_logger(__name__)  # get configured logger

load_dotenv()
imei_checker = ImeiCheckClient(os.getenv("IMEICHECK_NET_TOKEN"))


@bot.message_handler(commands=["start"])
@check_user_permissions(allowed_roles=["admin", "user"])
def send_welcome(message):
    bot.send_message(
        chat_id=message.chat.id,
        text="You started the bot!\n/help for available commands.",
    )


@bot.message_handler(commands=["help"])
@check_user_permissions(allowed_roles=["admin", "user"])
def send_help(message):
    help_header = "Here's the list of available commands:\n"
    commands = bot.get_my_commands()
    commands_text = "\n".join(
        [f"/{c.command} - {c.description}" for c in commands]
    )
    text = help_header + commands_text.replace("_", "\\_")
    bot.send_message(
        chat_id=message.chat.id,
        text=text,
    )


@bot.message_handler(commands=["add_user"])
@check_user_permissions(allowed_roles=["admin"])
def add_user(message: Message):
    try:
        _, tg_id, name = message.text.split()
        tg_id = int(tg_id)
        user_created = create_user(tg_id=tg_id, name=name)
        if user_created:
            text = f"User with id *{tg_id}* registered."
        else:
            text = "An error occurred during user registration."

    except ValueError:
        text = (
            "Incorrect command format. Use the following example:\n"
            "/add\\_user \\[telegram id] \\[user name]"
        )

    bot.send_message(
        chat_id=message.chat.id,
        text=text,
    )


@bot.message_handler(commands=["change_role"])
@check_user_permissions(allowed_roles=["admin"])
def change_user_role(message: Message):
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
        text = (
            "Incorrect command format. Use the following example:\n"
            "/change\\_role \\[telegram id] \\[new user role]"
        )
    bot.send_message(
        chat_id=message.chat.id,
        text=text,
    )


@bot.message_handler(commands=["change_status"])
@check_user_permissions(allowed_roles=["admin"])
def change_user_status(message: Message):
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
        text = (
            "Incorrect command format. Use the following example:\n"
            "/change\\_status \\[telegram id] \\[new user status]"
        )
    bot.send_message(
        chat_id=message.chat.id,
        text=text,
    )


@bot.message_handler(commands=["check_imei"])
@check_user_permissions(allowed_roles=["admin", "user"])
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

        text = (
            "Use the following example:\n"
            "/check\\_imei \\[IMEI] \\[service id]\n"
            "Where instead of service id will be the id of the service you need from "
            f"the table below:\n```id|price|title\n{text_rows}```"
        )
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
        text = (
            "Invalid command format, correct example:\n"
            "/check_imei [IMEI] [service id]"
        )
    except Exception as e:
        log.error(f"Error while checking IMEI: {e}")
        text = f"An error occurred: {str(e)}"

    bot.reply_to(
        message=message,
        text=text,
        parse_mode="html",
    )


@bot.message_handler(commands=["balance"])
@check_user_permissions(allowed_roles=["admin", "user"])
def check_balance(message: Message):
    balance = imei_checker.get_balance()
    service_name = imei_checker.get_service_name()
    bot.send_message(
        chat_id=message.chat.id,
        text=f"Service: *{service_name}*\nAccount balance: *{balance}*",
    )


@bot.message_handler(func=lambda message: True)
def handle_all_messages(message: Message):
    bot.reply_to(message=message, text="Unsupported command.")


if __name__ == "__main__":
    try:
        init_db()
        bot.set_my_commands(commands=bot_commands)
        log.info("The bot is running...")
        bot.polling(non_stop=True)
        # bot.infinity_polling()
    except Exception as e:
        log.error(f"Bot polling failed: {e}")
