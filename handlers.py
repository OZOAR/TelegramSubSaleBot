from telegram.ext import ConversationHandler
from telegram import (ReplyKeyboardMarkup,
                      ParseMode, InlineKeyboardMarkup,
                      InlineKeyboardButton)
from settings import TG_ADMIN_IDS, TG_SUPER_ADMIN_IDS
from glob import glob
from random import choice, randrange
from datetime import datetime
from emoji import emojize
from util import (parse_new_sub, get_keyboard, decode_table_name,
                  check_qiwi_payment, create_token, get_sub_price)

from sqlitedb_manager import (create_connection,
                              db_add_sub, db_select_subs, db_delete_sub, db_add_user,
                              get_user_subs, get_user, get_stock_sub, pay_for_sub,
                              give_sub, update_user_token, credit_user_account,
                              update_qiwi_params, get_qiwi_data, select_all_users)

from telegram_bot_pagination import InlineKeyboardPaginator


def start(bot, update):
    conn = create_connection()
    db_add_user(conn, bot.message.chat.id, bot.message.chat.first_name, bot.message.chat.last_name)
    random_num = randrange(100)
    smile = emojize('🥳', use_aliases=True)
    last_name = bot.message.chat.last_name
    if not bot.message.chat.last_name:
        last_name = ''
    bot.message.reply_text(f'''Поздравляем, *{bot.message.chat.first_name}* *{last_name}*! {smile}
Сегодня победу тебе принесло число *{random_num}*, скорее хватай свою подписку!

Твое место будет автоматически передано другому участнику в течении *10 минут*, если ты не воспользуешься своей скидкой!

Приятных покупок!''', parse_mode='Markdown', reply_markup=get_keyboard())


def show_command_list(bot, update):
    if bot.message.chat.id in TG_ADMIN_IDS:
        text = '<b>Список команд:</b>\n\n' \
               '/show - список подписок\n' \
               '/add - добавить новую подписку в базу\n' \
               '/del - удалить подписку из базы\n' \
               '/params - изменить платежные данные системы (доступно супер-админам)'
        update.bot.send_message(bot.message.chat.id, text=text,
                                parse_mode=ParseMode.HTML)
    else:
        update.bot.send_message(bot.message.chat.id, text='Извини, {}, но у тебя нет доступа к этой команде'
                                .format(bot.message.chat.first_name),
                                parse_mode=ParseMode.HTML)


def parrot(bot, update):
    update.bot.send_message(bot.message.chat.id, text=bot.message.text,
                            parse_mode=ParseMode.HTML, disable_web_page_preview=True)


def send_pricing(bot, update):
    update.bot.send_message(bot.message.chat.id, text='типа большой текст с описанием что да как, и цены и гарантия',
                            parse_mode=ParseMode.HTML, disable_web_page_preview=True)


def show_profile(bot, update):
    conn = create_connection()
    user = get_user(conn, bot.message.chat.id)
    text = '<b>Имя:</b> {}\n<b>Баланс:</b> {} руб\n<b>Дата регистрации:</b> {}\n----------------------------'\
        .format(user[2], user[5], user[4])
    update.bot.send_message(bot.message.chat.id, text=text,
                            parse_mode=ParseMode.HTML, disable_web_page_preview=True)
    subs = get_user_subs(conn, bot.message.chat.id)
    # subs= [{'sub_name': user[0], 'login': user[1], 'password': user[2], 'date':user[3]}]
    if subs:
        update.bot.send_message(bot.message.chat.id, text='''
        <b>Ваши покупки:</b>
        ''', parse_mode=ParseMode.HTML)
        for sub in subs:
            text = "<b>Сервис:</b> {sub_name}\n<b>Логин:</b> {login}\n" \
                   "<b>Пароль:</b> {password}\n".format(**sub)  # "<b>Дата:</b> {date}"
            update.bot.send_message(bot.message.chat.id, text=text,
                                    parse_mode=ParseMode.HTML, disable_web_page_preview=True)
    else:
        update.bot.send_message(bot.message.chat.id, text='<b>Купленных подписок нет!</b>', parse_mode=ParseMode.HTML)


def contact_support(bot, update):
    inl_keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton(text="Новости", url='https://t.me/kinoobum/3728')],
        [InlineKeyboardButton(text="Техподдержка", url='https://t.me/@mikhedova')],
        [InlineKeyboardButton(text='Гарантийный отдел', url='https://web.telegram.org/#/im?p=@Artprolead')]
    ])
    update.bot.send_message(bot.message.chat.id,
                            text="Техподдержка и гарантийный отдел",
                            reply_markup=inl_keyboard,
                            parse_mode=ParseMode.HTML
                            # disable_web_page_preview=True
                            )


def add_new_subs_start(bot, update):
    if bot.message.chat.id in TG_ADMIN_IDS:
        text = 'Уважаемый <b>{}</b>, введите данные для сервиса одной строкой, через пробелы, без символа " \n\n' \
               '<i>Пример:</i> "newlogin newpass 1" \n\n' \
               'Где: \n' \
               '<b>1</b> = <b>Netflix</b>\n' \
               '<b>2</b> = <b>Netflix HD</b>\n' \
               '<b>3</b> = <b>Disney</b>'.format(bot.message.chat.first_name)
        update.bot.send_message(bot.message.chat.id, text=text,
                                parse_mode=ParseMode.HTML)
        return "service_id"

    else:
        update.bot.send_message(bot.message.chat.id, text='Извини, {}, но у тебя нет доступа к этой команде'
                                .format(bot.message.chat.first_name),
                                parse_mode=ParseMode.HTML)
        return ConversationHandler.END  # выходим из диалога


def add_new_subs(bot, update):
    conn = create_connection()
    table_id = update.user_data['service_id'] = bot.message.text  # временно сохраняем ответ
    sub_list = parse_new_sub(table_id)
    if not sub_list:
        update.bot.send_message(bot.message.chat.id, text="Упс, произошла ошибка при добавлении",
                                parse_mode=ParseMode.HTML)
        conn.close()
        return ConversationHandler.END  # выходим из диалога
    result = db_add_sub(conn, login=sub_list[0], password=sub_list[1], table_id=sub_list[2])
    conn.close()
    if result:
        update.bot.send_message(bot.message.chat.id, text="Подписка успешно добавлена",
                                parse_mode=ParseMode.HTML)
    else:
        update.bot.send_message(bot.message.chat.id, text="Упс, произошла ошибка при добавлении",
                                parse_mode=ParseMode.HTML)
    return ConversationHandler.END  # выходим из диалога


def show_subs_start(bot, update):
    if bot.message.chat.id in TG_ADMIN_IDS:
        text = 'Уважаемый <b>{}</b>, введите номер сервиса \n\n' \
               'Номера: \n' \
               '<b>1</b> = <b>Netflix</b>\n' \
               '<b>2</b> = <b>Netflix HD</b>\n' \
               '<b>3</b> = <b>Disney</b>'.format(bot.message.chat.first_name)
        reply_keyboard = [["1", "2", "3"]]  # создаем клавиатуру
        update.bot.send_message(bot.message.chat.id, text=text,
                                parse_mode=ParseMode.HTML,
                                reply_markup=ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True,
                                                                 one_time_keyboard=True))
        print(21)
        return "service_id"
    else:
        update.bot.send_message(bot.message.chat.id, text='Извини, {}, но у тебя нет доступа к этой команде'
                                .format(bot.message.chat.first_name),
                                parse_mode=ParseMode.HTML)
        return ConversationHandler.END  # выходим из диалога


def show_subs(bot, update):
    table_id = update.user_data['id'] = bot.message.text  # временно сохраняем ответ
    if table_id not in ['1', '2', '3']:
        update.bot.send_message(bot.message.chat.id, text='Некорректный номер',
                                parse_mode=ParseMode.HTML)
        return ConversationHandler.END
    free_sub_count = 0
    conn = create_connection()
    sub_list = db_select_subs(conn, table_id)
    conn.close()
    text = f'<b>Подписки {decode_table_name(table_id)}</b>\n\n'
    if sub_list:
        print(sub_list)
        for sub in sub_list:
            text += f'<i><b>ID</b></i>: {sub[0]}\n<i><b>Логин</b></i>: {sub[1]}\n' \
                    f'<i><b>Пасс</b></i>: {sub[2]}\n<i><b>Владелец</b></i>: {sub[4]}\n' \
                    f'<i><b>Дата</b></i>: {sub[3]}\n\n'
            # update.bot.send_message(bot.message.chat.id, text=buffer, parse_mode=ParseMode.HTML)
            if sub[4] == 0:
                free_sub_count += 1
        update.bot.send_message(bot.message.chat.id, text=text, parse_mode=ParseMode.HTML)
        update.bot.send_message(bot.message.chat.id, text='Непроданных подписок: <b>{}</b> '.format(free_sub_count),
                                parse_mode=ParseMode.HTML,
                                reply_markup=get_keyboard())
        return ConversationHandler.END

    else:

        update.bot.send_message(bot.message.chat.id, text=f"А нет аккаунтов {decode_table_name(table_id)}</b>",
                                parse_mode=ParseMode.HTML)
        return ConversationHandler.END


def dont_know(bot, update):
    bot.message.reply_text("Я вас не понимаю!")


def delete_sub_start(bot, update):
    if bot.message.chat.id in TG_ADMIN_IDS:
        text = 'Уважаемый <b>{}</b>, введите номер сервиса для удаления записи\n\n' \
               'Номера: \n' \
               '<b>1</b> = <b>Netflix</b>\n' \
               '<b>2</b> = <b>Netflix HD</b>\n' \
               '<b>3</b> = <b>Disney</b>'.format(bot.message.chat.first_name)
        reply_keyboard = [["1", "2", "3"]]  # создаем клавиатуру
        update.bot.send_message(bot.message.chat.id, text=text,
                                parse_mode=ParseMode.HTML,
                                reply_markup=ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True, one_time_keyboard=True))
        return "service_id"
    else:
        update.bot.send_message(bot.message.chat.id, text='Извини, {}, но у тебя нет доступа к этой команде'
                                .format(bot.message.chat.first_name),
                                parse_mode=ParseMode.HTML)
        return ConversationHandler.END  # выходим из диалога


def delete_sub_get_service_id(bot, update):
    update.user_data['id'] = bot.message.text  # временно сохраняем ответ
    if update.user_data['id'] not in ['1', '2', '3']:
        update.bot.send_message(bot.message.chat.id, text='<b>Несуществующий выбор</b>', parse_mode=ParseMode.HTML)
        return ConversationHandler.END
    update.bot.send_message(bot.message.chat.id, text='Напиши номер <b>ID</b> подписки, которую нужно удалить',
                            parse_mode=ParseMode.HTML)

    return "service_row"  # ключ для определения следующего шага


def delete_sub_get_sub_id(bot, update):
    update.user_data['row'] = bot.message.text  # временно сохраняем ответ
    conn = create_connection()
    result = db_delete_sub(conn, update.user_data['id'], update.user_data['row'])
    if result:
        update.bot.send_message(bot.message.chat.id, text='Успешно удалено',
                                parse_mode=ParseMode.HTML)
        return ConversationHandler.END
    else:
        update.bot.send_message(bot.message.chat.id, text='Удалить не получилось\n'
                                                          'Скорее всего подписки с таким <b>ID</b> нет',
                                parse_mode=ParseMode.HTML)
        return ConversationHandler.END


def new_params_start(bot, update):
    if bot.message.chat.id in TG_SUPER_ADMIN_IDS:
        text = 'Уважаемый <b>{}</b>, введите номер параметра, который необходимо заменить\n\n' \
               'Номера: \n' \
               '<b>1</b> = <b>Qiwi акаунт</b>\n' \
               '<b>2</b> = <b>Qiwi API токен</b>'.format(bot.message.chat.first_name)
        reply_keyboard = [["1", "2"]]  # создаем клавиатуру
        update.bot.send_message(bot.message.chat.id, text=text,
                                parse_mode=ParseMode.HTML,
                                reply_markup=ReplyKeyboardMarkup(reply_keyboard,
                                                                 resize_keyboard=True,
                                                                 one_time_keyboard=True))
        return "param_id"
    else:
        update.bot.send_message(bot.message.chat.id, text='Извини, {}, но у тебя нет доступа к этой команде'
                                .format(bot.message.chat.first_name),
                                parse_mode=ParseMode.HTML)
        return ConversationHandler.END  # выходим из диалога


def get_new_params_id(bot, update):
    update.user_data['id'] = bot.message.text  # временно сохраняем ответ
    if update.user_data['id'] not in ['1', '2', '3']:
        update.bot.send_message(bot.message.chat.id, text='<b>Несуществующий выбор</b>', parse_mode=ParseMode.HTML)
        return ConversationHandler.END
    update.bot.send_message(bot.message.chat.id, text='Пришлите новое значени параметра:',
                            parse_mode=ParseMode.HTML)
    return "param_data"  # ключ для определения следующего шага


def get_new_params_data(bot, update):
    update.user_data['value'] = bot.message.text  # временно сохраняем ответ
    conn = create_connection()
    result = update_qiwi_params(conn, update.user_data['id'], update.user_data['value'])
    if result:
        update.bot.send_message(bot.message.chat.id, text='Параметр изменен успешно',
                                parse_mode=ParseMode.HTML)
        return ConversationHandler.END
    else:
        update.bot.send_message(bot.message.chat.id, text='Упс, произошла ошибка, обратитесь к Фахелю',
                                parse_mode=ParseMode.HTML)
        return ConversationHandler.END


def forward_post_start(bot, update):
    if bot.message.chat.id in TG_ADMIN_IDS:
        text = 'Присылай пост, который <b>разошлем</b> клиентам:\n\n'
        update.bot.send_message(bot.message.chat.id, text=text,
                                parse_mode=ParseMode.HTML)
        return "service_id"
    else:
        update.bot.send_message(bot.message.chat.id, text='Извини, {}, но у тебя нет доступа к этой команде'
                                .format(bot.message.chat.first_name),
                                parse_mode=ParseMode.HTML)
        return ConversationHandler.END  # выходим из диалога


def forward_post(bot, update):
    conn = create_connection()
    text = update.user_data['service_id'] = bot.message.text  # временно сохраняем ответ
    users = select_all_users(conn)

    if not users:
        update.bot.send_message(bot.message.chat.id, text="А рассылать то нет кому",
                                parse_mode=ParseMode.HTML)
        return ConversationHandler.END  # выходим из диалога
    print(1)
    inl_keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton(text=f"Все новинки тут", url='t.me/Artprolead')]
    ])
    for user_id in users:
        update.bot.send_message(user_id[1], text=text,
                                parse_mode=ParseMode.HTML, reply_markup=inl_keyboard, disable_web_page_preview=True)
    return ConversationHandler.END
    #     update.bot.send_message(bot.message.chat.id, text="Подписка успешно добавлена",
    #                             parse_mode=ParseMode.HTML)
    # else:
    #     update.bot.send_message(bot.message.chat.id, text="Упс, произошла ошибка при добавлении",
    #                             parse_mode=ParseMode.HTML)
    # return ConversationHandler.END  # выходим из диалога


def buy_subs_start(bot, update):
    image_list = glob('images/*')
    picture = choice(image_list)
    inl_keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("Netflix", callback_data='1')],
        [InlineKeyboardButton("Netflix HD", callback_data='2')],
        [InlineKeyboardButton("Disney", callback_data='3')]
    ])
    update.bot.send_photo(
        chat_id=bot.message.chat.id,
        photo=open(picture, 'rb'),
        caption="Выбирай подписку епт.",
        reply_markup=inl_keyboard
    )


def credit_balance(bot, update) -> None:
    conn = create_connection()
    # user = get_user(conn, bot.message.chat.id)
    # if user[6]:
    #     inl_keyboard = InlineKeyboardMarkup([
    #         [InlineKeyboardButton(text=f"Отменить оплату", callback_data='69')]
    #     ])
    #     bot.message.reply_text(
    #         f"<b>Пополнение счета</b>\n\n<b>Дата</b>:{datetime.now().replace(second=0, microsecond=0)}\n"
    #         f"<b>Статус</b>: Ожидается оплата {smile}\n\n"
    #         f"Пополните свой счет на любую сумму по номеру <b>QIWI</b>: {get_qiwi_data(conn)[1]}\n"
    #         f"<b>В комментарий к платежу укажите</b>: {token}\n\n",
    #         # f"<b>Убедительная просьба!</b>\nПосле QIWI перевода  ",
    #         # reply_markup=inl_keyboard,
    #         parse_mode=ParseMode.HTML
    #         )
    token = create_token()
    smile = emojize('⌛', use_aliases=True)
    search = emojize('🔎', use_aliases=True)
    print('Token = ', token)
    inl_keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton(text=f"Проверить оплату {search}", callback_data='69')]
    ])
    bot.message.reply_text(f"<b>Пополнение счета</b>\n\n<b>Дата</b>:{datetime.now().replace(second=0, microsecond=0)}\n"
                           f"<b>Статус</b>: Ожидается оплата {smile}\n\n"
                           f"Пополните свой счет на любую сумму по номеру <b>QIWI</b>: {get_qiwi_data(conn)[1]}\n"
                           f"<b>В комментарий к платежу укажите</b>: {token}\n\n", parse_mode=ParseMode.HTML)
    bot.message.reply_text('После перевода на <b>QIWI</b> кошелек нажмите на <b>кнопку</b>', reply_markup=inl_keyboard,
                           parse_mode=ParseMode.HTML)
    update_user_token(conn, bot.message.chat.id, token)


def inline_button_pressed(bot, update):
    query = bot.callback_query
    query.answer()
    print(query.data)
    if query.data in ['1', '2', '3']:
        table_id = query.data
        user_tg_id = query.message.chat.id
        conn = create_connection()
        sub_price = get_sub_price(table_id)
        sub = get_stock_sub(conn, table_id)
        print(f'BUY SUB \ntable_id: {table_id}\nuser_tg_id: {user_tg_id}\nsub_price: {sub_price}\nSub: {sub}\n')
        if sub:
            user = pay_for_sub(conn, user_tg_id, sub_price)
            print(f'user already buy!: {user}')
            print(user, ' - user')
            if user:
                give_sub(conn, table_id, sub, user_tg_id)
                print(sub[1], sub[2], sub[3])
                text = f'<i><b>Логин</b></i>: {sub[1]}\n<i><b>Пасс</b></i>: {sub[2]}\n' \
                       f'<i><b>Дата приобритения</b></i>: {sub[3]}\n\n'
                # f'<i><b>Владелец</b></i>:<a href=t.me/{user[1]}>{user[1]}\n</a>' \
                update.bot.edit_message_caption(
                    caption=text,
                    chat_id=query.message.chat.id,
                    message_id=query.message.message_id, parse_mode=ParseMode.HTML)

            else:
                update.bot.edit_message_caption(
                    caption='Нехватает денег на приобретение, проверьте ваш баланс в вашем <b>профиле</b>',
                    chat_id=query.message.chat.id,
                    message_id=query.message.message_id, parse_mode=ParseMode.HTML)
        else:
            inl_keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton(text="Техподдержка", url='https://t.me/Artprolead')]
            ])
            update.bot.edit_message_caption(
                chat_id=query.message.chat.id,
                caption="Упс, похоже закончились свободные аккаунты, "
                        "обратись в поддержку, там подскажут когда следующая партия ",
                reply_markup=inl_keyboard,
                message_id=query.message.message_id, parse_mode=ParseMode.HTML
            )
    elif query.data == '69':
        conn = create_connection()
        user_tg_id = query.message.chat.id
        user = get_user(conn, user_tg_id)
        user_last_token = user[6]
        user_balance = user[5]
        print(f'user {user_tg_id} checking payment.\nuser info: {user}\n')
        result = check_qiwi_payment(user_last_token)
        print(f'result is: {result}')
        done_smile = emojize('✔', use_aliases=True)
        if result:
            new_user_balance = user_balance + result
            print(f'new balance: {new_user_balance}')
            print(result)
            query.edit_message_text(
                text=f"<b>Пополнение счета</b>\n\n<b>Дата</b>:{datetime.now().replace(second=0, microsecond=0)}\n"
                     f"<b>Зачисленная сумма</b>: {result} <b>₽</b>\n\n"
                     f"<b>Статус</b>: Успешное пополнение {done_smile}\n\n",
                parse_mode=ParseMode.HTML
            )
            credit_user_account(conn, user_tg_id, new_user_balance, user_last_token)
        else:
            search = emojize('🔎', use_aliases=True)
            inl_keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton(text=f"Проверить оплату {search}", callback_data='69')]
            ])
            query.edit_message_text("<b>Платеж не обнаружен</b>\n\n"
                                    "Если проверка не дает результатов более <b>10 минут</b>, пожалуйста,\n"
                                    "свяжитесь с круглосуточной <a href='t.me/Artprolead'>службой поддержки!</a>",
                                    reply_markup=inl_keyboard,
                                    disable_web_page_preview=True,
                                    parse_mode=ParseMode.HTML
                                    )

    elif 'character#' in query.data:
        pass

