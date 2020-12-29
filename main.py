from telegram.ext import Updater,CommandHandler, MessageHandler, Filters, ConversationHandler
from settings import TG_TOKEN
from handlers import *

import logging

logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s',
                    level=logging.INFO,
                    filename='bot.log'
                    )
def main():
    my_bot = Updater(TG_TOKEN, use_context=True)
    logging.info('Start bot')
    my_bot.dispatcher.add_handler(CommandHandler('start', greating))
    # my_bot.dispatcher.add_handler(
    #     ConversationHandler(entry_points=[MessageHandler(Filters.regex('Заполнить анкету'), anketa_start)],
    #                         states={
    #                             "user_name": [MessageHandler(Filters.text, anketa_get_name)],
    #                             "user_age": [MessageHandler(Filters.text, anketa_get_age)],
    #                             "evaluation": [MessageHandler(Filters.regex('1|2|3|4|5'), anketa_get_evaluation)],
    #                             "comment": [MessageHandler(Filters.regex('Пропустить'), anketa_exit_comment),
    #                                         MessageHandler(Filters.text, anketa_comment)],
    #                         },
    #                         fallbacks=[MessageHandler(
    #                             Filters.text | Filters.video | Filters.photo | Filters.document, dontknow)]
    #                         )
    # )
    my_bot.dispatcher.add_handler(MessageHandler(Filters.regex('Начать'), parrot))
    my_bot.dispatcher.add_handler(MessageHandler(Filters.regex('Почему так дешево?'), send_pricing))
    my_bot.dispatcher.add_handler(MessageHandler(Filters.regex('Купить'), buy_subs))
    my_bot.dispatcher.add_handler(MessageHandler(Filters.regex('Покупки'), send_purchases))
    my_bot.dispatcher.add_handler(MessageHandler(Filters.regex('Техподержка 🔧'), contact_support))
    my_bot.dispatcher.add_handler(MessageHandler(Filters.text, parrot))
    my_bot.start_polling()
    my_bot.idle()


if __name__ == '__main__':
    main()