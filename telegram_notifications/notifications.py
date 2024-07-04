import os
import sys

import django
from django.conf import settings

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(PROJECT_ROOT)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "libro-borrow-api.settings")

from telegram import (
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    Update,
)
from telegram.constants import ParseMode
from telegram.ext import (
    CommandHandler,
    Application,
    ContextTypes,
    filters,
    MessageHandler,
    CallbackQueryHandler,
)

django.setup()

from borrowings.tasks import get_borrowings_for_user, get_overdue_for_user
from telegram_notifications.tasks import save_chat_id

print("Starting a bot....")


async def start_command(update, context):
    """Displays website button and borrowings buttons after selecting the /start command."""
    keyboard = [
        [
            InlineKeyboardButton("Website Library", url=settings.HOME_PAGE),
        ],
        [
            InlineKeyboardButton("Your borrowings", callback_data="view_borrowings"),
        ],
        [
            InlineKeyboardButton(
                "Overdue borrowings", callback_data="view_overdue_borrowings"
            ),
        ],
    ]
    user = update.effective_user
    reply_markup = InlineKeyboardMarkup(keyboard)

    chat_id = user.id
    connect_token = update.message.text.split(" ")[-1]
    if connect_token != "/start":
        save_chat_id.apply_async(args=[chat_id, connect_token])

    await update.message.reply_html(
        f"Hello {user.mention_html()}! Welcome to the Library.",
        reply_markup=reply_markup,
    )


async def callback_query_handler(update, context):
    """Handles 'Your borrowings' and 'Overdue borrowings' buttons"""
    query = update.callback_query
    user = query.from_user
    chat_id = user.id
    if query.data == "view_borrowings":
        result = get_borrowings_for_user.apply_async(args=[chat_id])
        borrowings = result.get()

        await query.answer()
        await query.edit_message_text(
            f"<b>Your borrowings:</b>\n<i>{borrowings}</i>", parse_mode=ParseMode.HTML
        )

    if query.data == "view_overdue_borrowings":
        result = get_overdue_for_user.apply_async(args=[chat_id])
        overdue_borrowings = result.get()

        await query.answer()
        await query.edit_message_text(
            f"<b>Overdue borrowings:</b>\n<i>{overdue_borrowings}</i>",
            parse_mode=ParseMode.HTML,
        )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Displays info on how to use the bot."""
    await update.message.reply_text("Use /start to open the options.")


async def text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Displays a message if the incoming command is not recognized."""
    await update.message.reply_text(
        "I don't understand you...Please select /start or /help"
    )


if __name__ == "__main__":
    application = Application.builder().token(settings.BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(MessageHandler(filters.TEXT | filters.COMMAND, text))
    application.add_handler(CallbackQueryHandler(callback_query_handler))

    application.run_polling(allowed_updates=Update.ALL_TYPES)
