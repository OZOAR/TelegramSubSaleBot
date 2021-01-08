# -*- coding: utf-8 -*-

from telegram import ReplyKeyboardMarkup, KeyboardButton
from datetime import datetime
import requests
import json
import re
from sqlitedb_manager import create_connection, get_qiwi_params
from settings import NETFLIX_PRICE, NETFLIX_HD_PRICE, DISNEY_PRICE,GMAIL_USER, GMAIL_PASSWORD, SMTP_SERVER_NAME
from smtplib import SMTP_SSL

SMILE_LIST = ['🙃','😂','😉','🤪','🤨']
CALLBACK_BUTTON_INFO = "⁉ Почему так дешево"
CALLBACK_BUTTON_PROFILE = "💼 Профиль"
CALLBACK_BUTTON_CREDIT = "💳 Пополнить счет"
CALLBACK_BUTTON_SUPPORT = "🔧 Техподержка"
CALLBACK_BUTTON_BUY = "📋 Купить подписку"


def get_main_keyboard():
    my_keyboard = ReplyKeyboardMarkup(
        [
            [CALLBACK_BUTTON_BUY],
            [CALLBACK_BUTTON_CREDIT],
            [CALLBACK_BUTTON_INFO],
            [CALLBACK_BUTTON_PROFILE, CALLBACK_BUTTON_SUPPORT]],
        resize_keyboard=True)
    # contact_button = KeyboardButton('Отправить контакты', request_contact=True)
    return my_keyboard


def get_service_price(service_id):
    service_id = str(service_id)
    a = {'1': NETFLIX_PRICE, '2': NETFLIX_HD_PRICE, '3': DISNEY_PRICE}
    return a[service_id]


def parse_new_sub(string):
    result = list(string.split(" "))
    if len(result) != 3:
        return False
    return result


def decode_table_name(table_id):
    table_id = str(table_id)
    a = {'1': 'Netflix', '2': 'Netflix HD', '3': 'Disney', '4': 'Nord VPN'}
    return a[table_id]


def create_token():
    now = datetime.now()
    date_list = [now.minute, now.second, now.microsecond]
    s = ''
    for date in date_list:
        s += str(date)
    return s[::-1]



def check_qiwi_payment(payment_token):
    s = requests.Session()
    conn = create_connection()
    qiwi_params = get_qiwi_params(conn)
    s.headers['authorization'] = 'Bearer ' + qiwi_params[2]
    parameters = {'rows': '50'}
    h = s.get('https://edge.qiwi.com/payment-history/v1/persons/' + qiwi_params[1] + '/payments', params=parameters)
    req = json.loads(h.text)
    for i in range(50):
        curr_comment = req['data'][i]['comment']
        if curr_comment:
            comment = re.search(payment_token, req['data'][i]['comment'])
            if comment:
                if comment.group(0) == payment_token:
                    return float(req['data'][i]['sum']['amount'])
                else:
                    return False
            else:
                return False


def form_sub_text(sub_list,length):
    finale_list = []
    while sub_list:
        buffer = ''
        sub_list_len = len(sub_list)
        if sub_list_len >= length and sub_list_len % length >= 0:
            counter = range(length)
        else:
            counter = range(sub_list_len)
        for i in counter:
            buffer += f"<b>ID</b>: {sub_list[i][0]}\n<b>Login</b>: {sub_list[i][1]}\n<b>Pass</b>: {sub_list[i][2]}\n" \
                      f"<b>Date</b>: {sub_list[i][3]}\n<b>Owner</b>: {sub_list[i][4]}\n\n"
        finale_list.append(buffer)
        sub_list = sub_list[:0] + sub_list[length:]
    return finale_list


def form_user_text(user_list, length):
    try_to_buy_count = 0
    finale_list = []
    user_num = 0
    while user_list:
        buffer = ''
        sub_list_len = len(user_list)
        if sub_list_len >= length and sub_list_len % length >= 0:
            counter = range(length)
        else:
            counter = range(sub_list_len)
        for i in counter:
            if user_list[i][7]:
                user_num += 1
                buffer += f'<b>#</b>{user_num}\n<b>tg_id</b>: {user_list[i][1]}\n' \
                          f'<b>Имя</b>: {user_list[i][2]} {user_list[i][3]}\n<b>username</b>: @{user_list[i][7]}\n\n'
            if user_list[i][6]:
                try_to_buy_count += 1
        finale_list.append(buffer)
        user_list = user_list[:0] + user_list[length:]
    return finale_list, try_to_buy_count


def send_email(subject, body):
    sent_from = GMAIL_USER
    to = [GMAIL_USER, ]
    email_text = f"""
    From: {sent_from}
    To: {", ".join(to)}
    Subject: {subject}

    {body}"""
    try:
        server = SMTP_SSL(SMTP_SERVER_NAME, 465)
        server.ehlo()
        server.login(GMAIL_USER, GMAIL_PASSWORD)
        server.sendmail(sent_from, to, email_text)
        server.close()
        return True
    except Exception as e:
        print('Email sending error: ', e)
        return False
