from telegram import ReplyKeyboardMarkup, KeyboardButton

SMILE_LIST = ['🙃','😂','😉','🤪','🤨']
CALLBACK_BUTTON_INFO = "Почему так дешево ⁉"
CALLBACK_BUTTON_PROFILE = "Покупки/Профиль 💼"
CALLBACK_BUTTON_SUPPORT = "Техподержка 🔧"
CALLBACK_BUTTON_BUY = "Купить подписку 📋"


def get_keyboard():
    # contact_button = KeyboardButton('Отправить контакты', request_contact=True)
    my_keyboard = ReplyKeyboardMarkup(
        [[CALLBACK_BUTTON_INFO], [CALLBACK_BUTTON_BUY],
        [CALLBACK_BUTTON_PROFILE, CALLBACK_BUTTON_SUPPORT]], resize_keyboard=True)
    return my_keyboard
