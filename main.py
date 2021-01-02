from telegram.ext import Updater,CommandHandler, MessageHandler, Filters, ConversationHandler, CallbackQueryHandler
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
    my_bot.dispatcher.add_handler(CommandHandler('list', show_command_list))
    my_bot.dispatcher.add_handler(
        ConversationHandler(entry_points=[MessageHandler(Filters.regex('/add'), add_new_subs_start)],
                            states={
                                "service_id": [MessageHandler(Filters.text, add_new_subs)],
                            },
                            fallbacks=[MessageHandler(Filters.regex('/add'), add_new_subs_start)]
                            )
    )
    my_bot.dispatcher.add_handler(
        ConversationHandler(entry_points=[MessageHandler(Filters.regex('/show'), show_subs_start)],
                            states={
                                "service_id": [MessageHandler(Filters.text, show_subs)],
                            },
                            fallbacks=[MessageHandler(Filters.regex('/show'), show_subs_start)]
                            )
    )
    my_bot.dispatcher.add_handler(
        ConversationHandler(entry_points=[MessageHandler(Filters.regex('/del'), delete_sub_start)],
                            states={
                                "service_id": [MessageHandler(Filters.text, delete_sub_get_service_id)],
                                "service_row": [MessageHandler(Filters.text, delete_sub_get_sub_id)],
                            },
                            fallbacks=[MessageHandler(Filters.regex('/del'), delete_sub_start)],

                            )
    )

    my_bot.dispatcher.add_handler(MessageHandler(Filters.regex('📋 Купить подписку'), buy_subs_start))
    my_bot.dispatcher.add_handler(MessageHandler(Filters.regex('⁉ Почему так дешево'), send_pricing))
    my_bot.dispatcher.add_handler(MessageHandler(Filters.regex('💼 Профиль'), show_profile))
    my_bot.dispatcher.add_handler(MessageHandler(Filters.regex('💳 Пополнить баланс'), top_up_balance))
    my_bot.dispatcher.add_handler(MessageHandler(Filters.regex('🔧 Техподержка'), contact_support))
    my_bot.dispatcher.add_handler(CallbackQueryHandler(inline_button_pressed))
    my_bot.dispatcher.add_handler(MessageHandler(Filters.text, parrot))
    my_bot.start_polling()
    my_bot.idle()


if __name__ == '__main__':
    main()