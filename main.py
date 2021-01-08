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
    my_bot.dispatcher.add_handler(CommandHandler('start', start))
    my_bot.dispatcher.add_handler(CommandHandler('stats', show_daily_stats))
    my_bot.dispatcher.add_handler(CommandHandler('list', show_command_list))
    my_bot.dispatcher.add_handler(
        ConversationHandler(entry_points=[MessageHandler(Filters.regex('/add'), add_sub_start)],
                            states={
                                "service_id": [MessageHandler(Filters.text, add_sub)],
                            },
                            fallbacks=[MessageHandler(
                                Filters.text | Filters.video | Filters.photo | Filters.document, dont_know)]
                            )
    )
    my_bot.dispatcher.add_handler(
        ConversationHandler(entry_points=[MessageHandler(Filters.regex('/show'), show_subs_start)],
                            states={
                                "service_id": [MessageHandler(Filters.text, show_subs)],
                            },
                            fallbacks=[MessageHandler(
                                Filters.text | Filters.video | Filters.photo | Filters.document, dont_know)]
                            )
    )
    my_bot.dispatcher.add_handler(
        ConversationHandler(entry_points=[MessageHandler(Filters.regex('/del'), delete_sub_start)],
                            states={
                                "service_id": [MessageHandler(Filters.text, delete_sub_get_params)],
                                "service_row": [MessageHandler(Filters.text, delete_sub)],
                            },
                            fallbacks=[MessageHandler(
                                Filters.text | Filters.video | Filters.photo | Filters.document, dont_know)],

                            )
    )
    # my_bot.dispatcher.add_handler(
    #     ConversationHandler(entry_points=[MessageHandler(Filters.regex('/params'), change_system_params_start)],
    #                         states={
    #                             "param_id": [MessageHandler(Filters.text, change_system_params_get_params)],
    #                             "param_data": [MessageHandler(Filters.text, change_system_params)],
    #                         },
    #                         fallbacks=[MessageHandler(
    #                             Filters.text | Filters.video | Filters.photo | Filters.document, dont_know)],
    #
    #                         )
    # )
    my_bot.dispatcher.add_handler(
        ConversationHandler(entry_points=[MessageHandler(Filters.regex('/send'), forward_post_start)],
                            states={
                                "service_id": [MessageHandler(Filters.text, forward_post)],
                            },
                            fallbacks=[MessageHandler(
                                Filters.text | Filters.video | Filters.photo | Filters.document, dont_know)]
                            )
    )
    my_bot.dispatcher.add_handler(MessageHandler(Filters.regex('📋 Купить подписку'), sell_sub_start))
    my_bot.dispatcher.add_handler(MessageHandler(Filters.regex('⁉ Почему так дешево'), send_pricing))
    my_bot.dispatcher.add_handler(MessageHandler(Filters.regex('💼 Профиль'), show_profile))
    my_bot.dispatcher.add_handler(MessageHandler(Filters.regex('💳 Пополнить счет'), credit_balance))
    my_bot.dispatcher.add_handler(MessageHandler(Filters.regex('🔧 Техподержка'), contact_support))
    my_bot.dispatcher.add_handler(MessageHandler(Filters.regex('🔧 Техподержка'), contact_support))
    my_bot.dispatcher.add_handler(CallbackQueryHandler(inline_button_pressed))
    # my_bot.dispatcher.add_handler(MessageHandler(Filters.text, parrot))
    my_bot.start_polling()
    my_bot.idle()


if __name__ == '__main__':
    main()