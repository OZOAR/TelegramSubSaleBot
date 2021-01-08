from telegram.ext import ConversationHandler
from telegram import (ReplyKeyboardMarkup,
                      ParseMode, InlineKeyboardMarkup,
                      InlineKeyboardButton)
from telegram import ChatMember
from settings import TG_ADMIN_IDS, TG_SUPER_ADMIN_IDS, NOTIFICATION_CHAT
from glob import glob
from random import choice, randint
from datetime import datetime
from emoji import emojize
from util import (parse_new_sub, get_main_keyboard, decode_table_name,
                  check_qiwi_payment, create_token, get_service_price,
                  form_sub_text, send_email, form_user_text)
from pprint import pprint

from sqlitedb_manager import *

from telegram_bot_pagination import InlineKeyboardPaginator


def start(bot, update):
    conn = create_connection()
    add_user(conn, bot.message.chat.id, bot.message.chat.first_name,
             bot.message.chat.last_name, bot.message.chat.username)
    random_num = randint(85,99)
    smile = emojize('🥳', use_aliases=True)
    last_name = bot.message.chat.last_name
    if bot.message.chat.id == -428898056:
        bot.message.reply_text('ага ага, чатик для тракнзакций значит!')
        return True
    if not bot.message.chat.last_name:
        last_name = ''
    gif_list = glob('gifs/timer_10_min.mp4')
    gif = choice(gif_list)
    print(gif_list)
    update.bot.send_animation(
        chat_id=bot.message.chat.id,
        caption=f'Поздравляем, <b>{bot.message.chat.first_name}</b> <b>{last_name}</b>! {smile}\n\n'
                f'Сегодня победу тебе принесло число <b>{random_num}</b>, скорее хватай свою подписку!\n\n'
                f'Твое место будет автоматически передано другому участнику в течении ❗️<b>10 минут</b>❗️, если ты не '
                f'воспользуешься своей скидкой!\n\nПриятных покупок!',
        animation=open(gif, 'rb'),
        parse_mode=ParseMode.HTML,
        width=200,
        height=200,
        reply_markup=get_main_keyboard()
    )


def show_command_list(bot, update):
    if bot.message.chat.id in TG_ADMIN_IDS:
        text = '<b>Список команд:</b>\n\n' \
               '/show - список подписок\n' \
               '/add - добавить новую подписку в базу\n' \
               '/del - удалить подписку из базы\n' \
               '/send - рассылает следующее сообщение всем клиентам'
        update.bot.send_message(bot.message.chat.id, text=text,
                                parse_mode=ParseMode.HTML)
    else:
        update.bot.send_message(bot.message.chat.id, text='Извини, {}, но у тебя нет доступа к этой команде'
                                .format(bot.message.chat.first_name),
                                parse_mode=ParseMode.HTML)


def force_subscribe(bot, update):

    look = emojize('👇', use_aliases=True)
    inl_keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton(text=f"Подписаться", url='')],
        [InlineKeyboardButton(text=f"Я подписался", callback_data='subscribe_complete')]
    ])
    bot.message.reply_text(
        f'{look} Это принудительная подписка, пока ты не подпишешься на наш канал не сможешь посмотреть функционал бота :)\n\n',
        parse_mode=ParseMode.HTML, reply_markup=inl_keyboard
    )

def parrot(bot, update):
    update.bot.send_message(bot.message.chat.id, text=bot.message.text,
                            parse_mode=ParseMode.HTML, disable_web_page_preview=True)


def send_pricing(bot, update):
    update.bot.send_message(bot.message.chat.id,
                            text=f'<b>@CinemaSubs_bot</b> - проект в первую очередь, про разумное использование ресурсов, в том числе - подписок на сервисы с нашими любимыми фильмами и сериалами.'
                                 f'\nНаша команда изучила принцип работы подписок на самых популярных платформах с контентом и нашла способ коллективного использования подписок, что в свою сторону серьезно уменьшает стоимость подписки для одного человека.\n'
                                 f'Главное правило: ❗️<b>НЕ МЕНЯТЬ ПАРОЛЬ</b>❗️\nПри изменении пороля гарантия на подписку <b>аннулируется</b> и Вам будет отказано в замене подписки!\n\n'
                                 f'В честь Нового Года мы запускаем <b>РАСПРОДАЖУ</b>со скидками до <b>70%</b> для первых <b>100</b> счастливчиков!!!\n\n'
                                 f'Пусть Новый 2021 радует Вас приятными событиями, а мы позаботимся о новом контенте! 😉\n\n'
                                 f'1. <b>Netflix Standart</b> <i>(для всех устройств, <b>используется на одного пользователя</b>)</i>\n'
                                 f'Наша цена: <b>249₽</b>\n'
                                 f'Цена на официальном сайте: <b>599₽</b>\n\n'
                                 f'2. <b>Netflix Premium HD 4K</b> <i>(для всех устройств, семейный доступ, <b>все новинки без ограничений</b>, доступен бонусный контент)</i>\n'
                                 f'Наша цена: <b>390₽</b>\n'
                                 f'Цена на официальном сайте: <b>999₽</b>\n\n'
                                 f'3. <b>Disney Plus</b> <i>(подписа на <b>2</b> года)</i>\n'
                                 f'Наша цена: <b>990₽</b>\n'
                                 f'Цена на официальном сайте: <b>5718₽/год</b>\n\n',
                            parse_mode=ParseMode.HTML, disable_web_page_preview=True, reply_markup=get_main_keyboard())


def show_profile(bot, update):
    conn = create_connection()
    user = get_user(conn, bot.message.chat.id)
    text = '<b>Имя:</b> {}\n<b>Баланс:</b> {} руб\n<b>Дата регистрации:</b> {}\n----------------------------'\
        .format(user[2], user[5], user[4])
    update.bot.send_message(bot.message.chat.id, text=text,
                            parse_mode=ParseMode.HTML, disable_web_page_preview=True)
    subs = get_user_subs(conn, bot.message.chat.id)
    print('subs: ',subs)
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
        [InlineKeyboardButton(text="Новости", url='https://t.me/joinchat/TpqbVRC8lt9_0Gcj')],
        [InlineKeyboardButton(text="Техподдержка", url='https://t.me/netflix_boss')],
    ])
    update.bot.send_message(bot.message.chat.id,
                            text="Техподдержка и гарантийный отдел",
                            reply_markup=inl_keyboard,
                            parse_mode=ParseMode.HTML
                            # disable_web_page_preview=True
                            )


def add_sub_start(bot, update):
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


def add_sub(bot, update):
    conn = create_connection()
    table_id = update.user_data['service_id'] = bot.message.text  # временно сохраняем ответ
    sub_list = parse_new_sub(table_id)
    print(sub_list)
    if not sub_list:
        update.bot.send_message(bot.message.chat.id, text="Упс, произошла ошибка при добавлении",
                                parse_mode=ParseMode.HTML)
        return ConversationHandler.END  # выходим из диалога
    result = add_service_sub(conn, login=sub_list[0], password=sub_list[1], table_id=sub_list[2])
    print(result)
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
    sub_list = select_subs(conn, table_id)
    decoded_table_name = decode_table_name(table_id)
    if not sub_list:
        update.bot.send_message(bot.message.chat.id, text=f"А нет аккаунтов <b>{decoded_table_name}</b>",
                                parse_mode=ParseMode.HTML)
        return ConversationHandler.END
    update.bot.send_message(bot.message.chat.id,
                            text=f'<b>Подписки {decoded_table_name}</b>\n\n',
                            parse_mode=ParseMode.HTML)
    for sub in sub_list:

        if sub[4] == 0:
            free_sub_count += 1
    formed_list = form_sub_text(sub_list, 5)
    sub = formed_list[0]
    paginator = InlineKeyboardPaginator(
        len(formed_list),
        data_pattern='character#{page}#'+str(table_id)
    )
    update.bot.send_message(chat_id=bot.message.chat.id,
                            text=sub,
                            reply_markup=paginator.markup,
                            parse_mode=ParseMode.HTML)
    update.bot.send_message(bot.message.chat.id, text=f'<b>Всего</b>: {len(sub_list)}\n<b>Непроданных</b>: {free_sub_count}',
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


def delete_sub_get_params(bot, update):
    update.user_data['id'] = bot.message.text  # временно сохраняем ответ
    if update.user_data['id'] not in ['1', '2', '3']:
        update.bot.send_message(bot.message.chat.id, text='<b>Несуществующий выбор</b>', parse_mode=ParseMode.HTML)
        return ConversationHandler.END
    update.bot.send_message(bot.message.chat.id, text='Напиши номер <b>ID</b> подписки, которую нужно удалить',
                            parse_mode=ParseMode.HTML)

    return "service_row"  # ключ для определения следующего шага


def delete_sub(bot, update):
    update.user_data['row'] = bot.message.text  # временно сохраняем ответ
    conn = create_connection()
    print(bot.message.text)
    result = delete_db_sub(conn, update.user_data['id'], update.user_data['row'])
    print(result)
    if result:
        update.bot.send_message(bot.message.chat.id, text='Успешно удалено',
                                parse_mode=ParseMode.HTML)
        return ConversationHandler.END
    else:
        update.bot.send_message(bot.message.chat.id, text='Удалить не получилось\n'
                                                          'Скорее всего подписки с таким <b>ID</b> нет',
                                parse_mode=ParseMode.HTML)
        return ConversationHandler.END

#
# def change_system_params_start(bot, update):
#     if bot.message.chat.id in TG_SUPER_ADMIN_IDS:
#         text = 'Уважаемый <b>{}</b>, введите номер параметра, который необходимо заменить\n\n' \
#                'Номера: \n' \
#                '<b>1</b> = <b>Qiwi акаунт</b>\n' \
#                '<b>2</b> = <b>Qiwi API токен</b>'.format(bot.message.chat.first_name)
#         reply_keyboard = [["1", "2"]]  # создаем клавиатуру
#         update.bot.send_message(bot.message.chat.id, text=text,
#                                 parse_mode=ParseMode.HTML,
#                                 reply_markup=ReplyKeyboardMarkup(reply_keyboard,
#                                                                  resize_keyboard=True,
#                                                                  one_time_keyboard=True))
#         return "param_id"
#     else:
#         update.bot.send_message(bot.message.chat.id, text='Извини, {}, но у тебя нет доступа к этой команде'
#                                 .format(bot.message.chat.first_name),
#                                 parse_mode=ParseMode.HTML)
#         return ConversationHandler.END  # выходим из диалога
#
#
# def change_system_params_get_params(bot, update):
#     update.user_data['id'] = bot.message.text  # временно сохраняем ответ
#     if update.user_data['id'] not in ['1', '2', '3']:
#         update.bot.send_message(bot.message.chat.id, text='<b>Несуществующий выбор</b>', parse_mode=ParseMode.HTML)
#         return ConversationHandler.END
#     update.bot.send_message(bot.message.chat.id, text='Пришлите новое значени параметра:',
#                             parse_mode=ParseMode.HTML)
#     return "param_data"  # ключ для определения следующего шага
#
#
# def change_system_params(bot, update):
#     update.user_data['value'] = bot.message.text  # временно сохраняем ответ
#     conn = create_connection()
#     print(update.user_data['value'])
#     print(update.user_data['id'])
#     result = update_qiwi_params(conn, update.user_data['id'], update.user_data['value'])
#     if result:
#         update.bot.send_message(bot.message.chat.id, text='Параметр изменен успешно',
#                                 parse_mode=ParseMode.HTML)
#         return ConversationHandler.END
#     else:
#         update.bot.send_message(bot.message.chat.id, text='Упс, произошла ошибка, обратитесь к Фахелю',
#                                 parse_mode=ParseMode.HTML)
#         return ConversationHandler.END


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
    users = get_all_users(conn)

    if not users:
        update.bot.send_message(bot.message.chat.id, text="А рассылать то нет кому",
                                parse_mode=ParseMode.HTML)
        return ConversationHandler.END  # выходим из диалога
    inl_keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton(text=f"Все новинки тут", url='t.me/Artprolead')]
    ])
    for user_id in users:
        update.bot.send_message(user_id[1], text=text,
                                parse_mode=ParseMode.HTML, disable_web_page_preview=True)
    return ConversationHandler.END
    #     update.bot.send_message(bot.message.chat.id, text="Подписка успешно добавлена",
    #                             parse_mode=ParseMode.HTML)
    # else:
    #     update.bot.send_message(bot.message.chat.id, text="Упс, произошла ошибка при добавлении",
    #                             parse_mode=ParseMode.HTML)
    # return ConversationHandler.END  # выходим из диалога


def sell_sub_start(bot, update):
    image_list = glob('images/netflix_disney.jpg')
    # picture = choice(image_list)
    inl_keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton(f"Netflix  •  {get_service_price('1')}₽", callback_data='1')],
        [InlineKeyboardButton(f"Netflix HD 4K  •  {get_service_price('2')}₽", callback_data='2')],
        [InlineKeyboardButton(f"Disney+  •  {get_service_price('3')}₽", callback_data='3')]
    ])
    update.bot.send_photo(
        chat_id=bot.message.chat.id,
        photo=open(image_list[0], 'rb'),
        caption="Выберите стриминговый сервис для совершения покупки.\n"
                "После совершшения покупки вы получите данные для входа в личный кабинет "
                "учетной записи стримингового сервиса.\n\n"
                "Список всех ваших покупок, а также текущий баланс вы можете посмотреть в разделе  💼 <b>Профиль</b>\n\n"
                "❗️<b>РОЖДЕСТВЕНСКАЯ РАСПРОДАЖА</b>❗️\n\n<b>Только сегодня!</b>\n"
                "Наши цены снижены более чем на <b>30%</b>\n\n"
                "<b>Netflix</b>\n"
                f"Ация: <s>249₽</s> <b>{get_service_price('1')}₽</b>\n\n"
                "<b>Netflix HD 4K</b>\n"
                f"Ация: <s>390₽</s> <b>{get_service_price('2')}₽</b>\n\n"
                "<b>Disney+</b>\n"
                f"Ация: <s>990₽</s> <b>{get_service_price('3')}₽</b>\n\n",
        reply_markup=inl_keyboard, parse_mode=ParseMode.HTML
    )


def credit_balance(bot, update) -> None:
    conn = create_connection()
    user = get_user(conn, bot.message.chat.id)
    present_toke = user[6]
    pending = emojize('⌛', use_aliases=True)
    search = emojize('🔎', use_aliases=True)
    cancel = emojize('🧨', use_aliases=True)
    if present_toke != 0:
        inl_keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton(text=f"Получить новый токен {cancel}", callback_data='68')],
            [InlineKeyboardButton(text=f"Проверить оплату {search}", callback_data='69')]
        ])
        bot.message.reply_text(
            f'У вас имеется <b>токен</b>: <b><code>{present_toke}</code></b> для пополнения вашего счета.\n\n'
            f'Если по какой либо причине вам необходим <b>новый токен</b> для пополнения счета выберите '
            f'<b>Получить новый токен {cancel}</b>\n\n'
            f'Учтите, если вы получите <b>новый токен</b>, все неподтвержденые Qiwi переводы '
            f'содержащие ваш нынешний токен <code>{present_toke}</code> зачислены <b>не будут</b>.',
            parse_mode=ParseMode.HTML, reply_markup=inl_keyboard
            )
    else:
        token = create_token()
        inl_keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton(text=f"Проверить оплату {search}", callback_data='69')]
        ])
        qiwi_params = get_qiwi_params(conn)
        print(qiwi_params)
        bot.message.reply_text(f"<b>Пополнение счета</b>\n\n<b>Дата</b>: "
                               f"{datetime.now().replace(second=0, microsecond=0)}\n"
                               f"<b>Статус</b>: Не подтверждено {pending}\n\n"
                               f"Пополните свой счет на любую сумму по номеру <b>QIWI</b>:\n"
                               f"<code>{qiwi_params[1]}</code>\n"
                               f"Или совершите перевод на карту <b>VISA</b>:\n"
                               f"<code>{qiwi_params[3]}</code>\n"
                               f"Действует до: <code>{qiwi_params[4]}</code>\n\n"
                               f"<b>В комментарий</b> к платежу укажите:\n"
                               f"<code>{token}</code>", parse_mode=ParseMode.HTML)
        bot.message.reply_text('После перевода на <b>QIWI</b> кошелек нажмите на <b>кнопку</b>', reply_markup=inl_keyboard,
                               parse_mode=ParseMode.HTML)
        update_user_token(conn, bot.message.chat.id, token)


def inline_button_pressed(bot, update):
    query = bot.callback_query
    query.answer()
    query_data = query.data
    user_tg_id = query.message.chat.id
    conn = create_connection()
    if query_data in ['1', '2', '3']:
        table_id = query_data
        sub_price = get_service_price(table_id)
        sub = get_free_sub(conn, table_id)
        print(f'BUY SUB \ntable_id: {table_id}\nuser_tg_id: {user_tg_id}\nsub_price: {sub_price}\nSub: {sub}\n')
        if sub:
            result = pay_for_sub(conn, user_tg_id, sub_price)
            # print(result, ' - user')
            if result:
                give_sub_to_user(conn, table_id, sub, user_tg_id)
                user = get_user(conn, user_tg_id)
                print(user)
                log_sale_transaction(conn, user_tg_id, user[2], user[3], user[7], table_id)
                text = f'<i><b>Логин</b></i>: {sub[1]}\n<i><b>Пасс</b></i>: {sub[2]}\n' \
                       f'<i><b>Дата приобритения</b></i>: {sub[3]}\n\n'
                email_subject = 'Purchase made !'
                email_body = f'User: {user[2]} / @{user[7]}\n\nPurchased a subscription *{decode_table_name(table_id)}* #{sub[0]}'
                send_email(email_subject, email_body)
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
                [InlineKeyboardButton(text="Техподдержка", url='https://t.me/netflix_boss')]
            ])
            update.bot.edit_message_caption(
                chat_id=query.message.chat.id,
                caption="Упс, похоже закончились свободные аккаунты, "
                        "обратись в поддержку, там подскажут когда следующая партия ",
                reply_markup=inl_keyboard,
                message_id=query.message.message_id, parse_mode=ParseMode.HTML
            )
    # сброс токена
    if query_data == '68':
        user_tg_id = query.message.chat.id
        update_user_token(conn, user_tg_id, 0)
        query.edit_message_text(
            text='<b>Пополенине счета отменено</b>\n\n'
                 'Для получения данных для пополнения вашего счета выбирете пункт меню - 💳 Пополнить счет',
            parse_mode=ParseMode.HTML
        )
    # пополнение баланса
    if query_data == '69':
        user = get_user(conn, user_tg_id)
        user_last_token = user[6]
        user_balance = user[5]
        print(f'user {user_tg_id} checking payment.\nuser info: {user}\n')
        result = check_qiwi_payment(user_last_token)
        # print('payment result',result)
        # result = 10
        print(f'result is: {result}')
        done_smile = emojize('✔️', use_aliases=True)
        if result:
            new_user_balance = user_balance + result
            print(f'new balance: {new_user_balance}')
            query.edit_message_text(
                text=f"<b>Пополнение счета</b>\n\n<b>Дата</b>:{datetime.now().replace(second=0, microsecond=0)}\n"
                     f"<b>Зачисленная сумма</b>: {result} <b>₽</b>\n\n"
                     f"<b>Статус</b>: Успешное пополнение {done_smile}\n\n",
                parse_mode=ParseMode.HTML)
            credit_user_account(conn, user_tg_id, new_user_balance, user_last_token)
            update_user_token(conn, user_tg_id, 0)
            log_credit_transaction(conn, user_tg_id, user[2], user[3], user[7], result)
            email_subject = 'Balance replenishment'
            email_body = f'User: {user[2]} / @{user[7]}\n\nReplenished the balance on *{result}* rub'
            send_email(email_subject, email_body)
        else:
            search = emojize('🔎', use_aliases=True)
            inl_keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton(text=f"Проверить оплату {search}", callback_data='69')]])
            query.edit_message_text("<b>Платеж не обнаружен</b>\n\n"
                                    "Если проверка не дает результатов более <b>10 минут</b>, пожалуйста,\n"
                                    "свяжитесь с круглосуточной <a href='t.me/Artprolead'>службой поддержки!</a>",
                                    reply_markup=inl_keyboard,
                                    disable_web_page_preview=True,
                                    parse_mode=ParseMode.HTML)

    if 'character#' in query.data:
        page = int(query.data.split('#')[1])
        table_id = query.data.split('#')[2]
        sub_list = select_subs(conn, table_id)
        formed_list = form_sub_text(sub_list, 5)
        paginator = InlineKeyboardPaginator(
            len(formed_list),
            current_page=page,
            data_pattern='character#{page}#'+str(table_id))
        sub = formed_list[page - 1]
        query.edit_message_text(
            text=sub,
            reply_markup=paginator.markup,
            parse_mode=ParseMode.HTML)

    if 'daily_users#' in query.data:
        page = int(query.data.split('#')[1])
        today_date = date.today().strftime("%d/%m/%Y")
        user_list = get_user_by_date(conn, today_date)
        result = form_user_text(user_list, 10)
        formed_list = result[0]

        paginator = InlineKeyboardPaginator(
            len(formed_list),
            current_page=page,
            data_pattern='daily_users#{page}')
        users = formed_list[page - 1]
        query.edit_message_text(
            text=users,
            reply_markup=paginator.markup,
            parse_mode=ParseMode.HTML)


def show_daily_stats(bot, update):
    if bot.message.chat.id in TG_ADMIN_IDS:
        conn = create_connection()
        today_date = date.today().strftime("%d/%m/%Y")
        credit_list = get_credit_transaction_by_date(conn, today_date)
        sale_list = get_sale_log_by_date(conn, today_date)
        user_list = get_user_by_date(conn, today_date)
        text = ''
        total_sum = 0

        if credit_list:
            print('credits: ', credit_list)
            for i in range(len(credit_list)):
                text += f'<b>#</b>{i+1}\n<b>tg_id</b>: {credit_list[i][1]}\n' \
                        f'<b>Имя</b>: {credit_list[i][2]} {credit_list[i][3]}\n<b>username</b>: {credit_list[i][4]}\n' \
                        f'<b>Сумма</b>: {credit_list[i][6]}\n\n'
                total_sum += credit_list[i][6]
        update.bot.send_message(bot.message.chat.id, text=f'<b>Пополнения за</b> {today_date}\n\n'+text+
                                                          f'\n\n<b>Общая сумма пополнения</b>: {total_sum}',
                                parse_mode=ParseMode.HTML)
        text = ''
        if sale_list:
            for i in range(len(sale_list)):
                text += f'<b>#</b>{i+1}\n<b>tg_id</b>: {sale_list[i][1]}\n' \
                        f'<b>Имя</b>: {sale_list[i][2]} {sale_list[i][3]}\n<b>username</b>: {sale_list[i][4]}\n' \
                        f'<b>Сервис</b>: {decode_table_name(sale_list[i][6])}\n\n'
        update.bot.send_message(bot.message.chat.id, text=f'<b>Продажи за</b> {today_date}\n\n'+text+
                                                          f'\n\n<b>Продано пописок</b>: {len(sale_list)}',
                                parse_mode=ParseMode.HTML)
        update.bot.send_message(bot.message.chat.id, text=f'<b>Новые клиенты за</b> {today_date}\n\n'
                                                          f'Отображаем только клиентов с @username',
                                parse_mode=ParseMode.HTML)
        if user_list:
            result = form_user_text(user_list, 10)
            formed_list = result[0]
            users = formed_list[0]
            paginator = InlineKeyboardPaginator(
                len(formed_list),
                data_pattern='daily_users#{page}'
            )
            update.bot.send_message(chat_id=bot.message.chat.id,
                                    text=users,
                                    reply_markup=paginator.markup,
                                    parse_mode=ParseMode.HTML)
            update.bot.send_message(bot.message.chat.id,
                                    text=f'<b>Итого новых клиентов</b>: {len(user_list)}\n',
                                    parse_mode=ParseMode.HTML)
            # for i in range(len(user_list)):
            #     if user_list[i][6] or user_list[i][7]:
            #         update.bot.send_message(bot.message.chat.id,
            #                                 text=f'<b>#</b>{i + 1}\n<b>tg_id</b>: {user_list[i][1]}\n'
            #                                      f'<b>Имя</b>: {user_list[i][2]} {user_list[i][3]}\n'
            #                                      f'<b>username</b>: {user_list[i][7]}\n\n',
            #                                 parse_mode=ParseMode.HTML)

        update.bot.send_message(bot.message.chat.id, text=f'\n\n<b>Пробовали купить</b>: {result[1]}',
                                parse_mode=ParseMode.HTML)

    else:
        update.bot.send_message(bot.message.chat.id, text='Извини, {}, но у тебя нет доступа к этой команде'
                                .format(bot.message.chat.first_name),
                                parse_mode=ParseMode.HTML)