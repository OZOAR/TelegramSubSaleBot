import os
import logging

from telegram import InlineKeyboardButton, ParseMode
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler
from telegram_bot_pagination import InlineKeyboardPaginator

character_pages = [(11, 'ebat`@yee.com', 'ehwbwhw', '0', 1478376263),
                   (12, 'ghsfghn@gee.ru', 'ehwbwhw', '0', 1478376263),
                   (13, 'Rif@gee.ru', 'ehwbwhw', '0', 1478376263),
                   (14, 'Newone@hee.tu', 'ehwvwg', '0', 1478376263),
                   (15, 'Yidzfzdhff@gee.ru', 'ehwbwhw', '0', 1478376263),
                   (16, 'Fewone@hee.tu', 'ehwvwg', '0', 1478376263),
                   (17, 'Fewone@hee.tu', 'ehwvwg', '0', 1478376263),
                   (18, 'Fewone@hee.tu', 'ehwvwg', '0', 1478376263),
                   (19, 'Fewone@hee.tu', 'ehwvwg', '0', 1478376263)]


def start(update, context):

    paginator = InlineKeyboardPaginator(
        len(character_pages),
        data_pattern='character#{page}'
    )
    char = character_pages[0]
    text = f"*ID*: {char[0]}\n*Login*: {char[1]}\n*Pass*: {char[2]}\n*Date*: {char[3]}\n*Owner*: {char[4]}"
    update.message.reply_text(
        text=text,
        reply_markup=paginator.markup,
        parse_mode=ParseMode.HTML
    )


def characters_page_callback(update, context):
    query = update.callback_query
    query.answer()
    page = int(query.data.split('#')[1])

    paginator = InlineKeyboardPaginator(
        len(character_pages),
        current_page=page,
        data_pattern='character#{page}'
    )

    text = f"*ID*: {char[0]}\n*Login*: {char[1]}\n*Pass*: {char[2]}\n*Date*: {char[3]}\n*Owner*: {char[4]}"
    query.edit_message_text(
        text=character_pages[page - 1],
        reply_markup=paginator.markup,
        parse_mode='Markdown'
    )

updater = Updater(('1297957924:AAEkt1nMyW0cYqvexeOoXBsCVXN-Vkn4liQ'), use_context=True)

updater.dispatcher.add_handler(CommandHandler('start', start))
updater.dispatcher.add_handler(CallbackQueryHandler(characters_page_callback, pattern='^character#'))

updater.start_polling()
updater.idle()