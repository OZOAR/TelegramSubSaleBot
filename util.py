from telegram import ReplyKeyboardMarkup, KeyboardButton
from datetime import datetime
import requests
import json
import re
from settings import QIWI_TOKEN, QIWI_ACCOUNT, NETFLIX_PRICE, NETFLIX_HD_PRICE, DISNEY_PRICE

SMILE_LIST = ['🙃','😂','😉','🤪','🤨']
CALLBACK_BUTTON_INFO = "⁉ Почему так дешево"
CALLBACK_BUTTON_PROFILE = "💼 Профиль"
CALLBACK_BUTTON_TOPUP = "💳 Пополнить баланс"
CALLBACK_BUTTON_SUPPORT = "🔧 Техподержка"
CALLBACK_BUTTON_BUY = "📋 Купить подписку"


def get_keyboard():
    # contact_button = KeyboardButton('Отправить контакты', request_contact=True)
    my_keyboard = ReplyKeyboardMarkup(
        [[CALLBACK_BUTTON_INFO], [CALLBACK_BUTTON_BUY],[CALLBACK_BUTTON_TOPUP],
        [CALLBACK_BUTTON_PROFILE, CALLBACK_BUTTON_SUPPORT]], resize_keyboard=True)
    return my_keyboard



def get_sub_price(service_id):
    service_id = str(service_id)
    a = {'1': NETFLIX_PRICE, '2': DISNEY_PRICE, '3': NETFLIX_HD_PRICE}
    return a[service_id]


def parse_new_sub(string):
    result = list(string.split(" "))
    if len(result) != 3:
        return False
    return result


def decode_table_name(table_id):
    table_id = str(table_id)
    a = {'1':'Netflix', '2':'Netflix HD','3':'Disney'}
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
    s.headers['authorization'] = 'Bearer ' + QIWI_TOKEN
    parameters = {'rows': '50'}
    h = s.get('https://edge.qiwi.com/payment-history/v1/persons/' + QIWI_ACCOUNT + '/payments', params=parameters)
    req = json.loads(h.text)
    comment = re.search(payment_token, req['data'][0]['comment'])

    if req['data'][0]['account'] == QIWI_ACCOUNT and comment:
        return float(req['data'][0]['sum']['amount'])
    else:
        return False
