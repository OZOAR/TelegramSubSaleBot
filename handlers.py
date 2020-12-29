from util import get_keyboard
import requests
from telegram.ext import ConversationHandler
from telegram import ReplyKeyboardRemove, ReplyKeyboardMarkup, ParseMode, InlineKeyboardMarkup, InlineKeyboardButton
from bs4 import BeautifulSoup
from glob import glob
from random import choice
from emoji import emojize
from util import SMILE_LIST

def greating(bot, update):
    smile = emojize(choice(SMILE_LIST), use_aliases=True)
    bot.message.reply_text('Рад приветствовать, Вас, {}, тут произойдет розыгрыш {} '
                           .format(bot.message.chat.first_name, smile), reply_markup=get_keyboard())


def parrot(bot, update):
    print(bot.message.chat.id)
    update.bot.send_message(bot.message.chat.id, text=bot.message.text,
                            parse_mode=ParseMode.HTML, disable_web_page_preview=True)


def send_pricing(bot, update):
    update.bot.send_message(bot.message.chat.id, text='типа большой текст с описанием что да как, и цены и гарантия',
                            parse_mode=ParseMode.HTML,disable_web_page_preview=True)


def buy_subs(bot, update):

    inl_keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton(text="Подписка ivi", url='https://web.telegram.org/#/im?p=@news_shopsmsbot')],
        [InlineKeyboardButton(text="Подписка Netflix", url='https://t.me/@mikhedova')],
        [InlineKeyboardButton(text='Подписка Disney', url='https://web.telegram.org/#/im?p=@Artprolead')]
    ])
    image_list = glob('images/*')
    picture = choice(image_list)
    update.bot.send_photo(
        chat_id=bot.message.chat.id,
        photo=open(picture, 'rb'),
        caption="Что покупать будешь, малец ?",
        reply_markup=inl_keyboard
    )

def send_purchases(bot, update):
    list_of_purchaises = [{'ivi':{
        "date_ivi": '31.12.2020',
        "login_ivi": 'admin',
        "password_ivi": '123'
    }},
    {'netflix':{
        "date_netflix": '31.12.2020',
        "login_netflix": 'admin',
        "password_netflix": '123'
    }},
    {'disney':{
        "date_disney": '31.12.2020',
        "login_disney": 'admin',
        "password_disney": '123'
    }}]
    if list_of_purchaises:
        update.bot.send_message(bot.message.chat.id, text='<b>Ваши покупки:</b>',parse_mode=ParseMode.HTML)
        for purchaise in list_of_purchaises:
            text = """:
                    <b><i>Подписка ivi</i></b>
                    <b>Куплено:</b> {date_ivi}
                    <b>Логин:</b> {login_ivi}
                    <b>Пароль:</b> {password_ivi}
                    
                    <b><i>Подписка Netflix</i></b>
                    <b>Куплено:</b> {date_netflix}
                    <b>Логин:</b> {login_netflix}
                    <b>Пароль:</b> {password_netflix}
                    
                    <b><i>Подписка Disney</i></b>
                    <b>Куплено:</b> {date_Disney}
                    <b>Логин:</b> {login_Disney}
                    <b>Пароль:</b> {password_Disney}
                    """.format(**purchaise)
            update.bot.send_message(bot.message.chat.id, text=text,
                            parse_mode=ParseMode.HTML,disable_web_page_preview=True)
    else:
        update.bot.send_message(bot.message.chat.id, text='<b>Купленных подписок нет!</b>',parse_mode=ParseMode.HTML)


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


def inline_button_pressed(bot, update):
    query = bot.callback_query
    data = int(query.data)
    update.bot.edit_message_caption(
        caption="Спасибо за ваш голос",
        chat_id=query.message.chat.id,
        message_id=query.message.message_id)
