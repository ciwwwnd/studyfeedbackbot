from typing import Any
import telebot
from telebot import types
import ruz
import re
import os

token = os.environ['TOKEN']
bot = telebot.TeleBot(token)


@bot.message_handler(commands=['start'])
def starting(message):
    # keyboard = types.InlineKeyboardMarkup()
    # # callback_button = types.InlineKeyboardButton(text="Оставить отзыв", callback_data="geek")
    # keyboard.add(callback_button)
    email = bot.send_message(message.chat.id,
                             "Привет! Я люблю собирать обратную связь, это моя работа. Пожалуйста, напишите свой адрес корпоративной почты.")
    bot.register_next_step_handler(email, check_email)


@bot.message_handler(content_types=["text"])
def any_msg(message):
    keyboard = types.InlineKeyboardMarkup()
    callback_math = types.InlineKeyboardButton(text="Discrete mathematics", callback_data="professor")
    callback_cs50 = types.InlineKeyboardButton(text="Introduction to Computer Science", callback_data="professor")
    callback_biology = types.InlineKeyboardButton(text="Nuclear biology", callback_data="professor")
    keyboard.add(callback_math)
    keyboard.add(callback_cs50)
    keyboard.add(callback_biology)
    bot.send_message(message.chat.id, "Выбери свой предмет из списка", reply_markup=keyboard)


global schedule


def check_email(message):
    global schedule
    pttrn = ",\s'text':\s'([^']+)"
    mail = re.findall(pttrn, str(message))[0]
    check = ruz.utils.is_valid_hse_email(mail)
    if not check:
        msg = bot.send_message(message.chat.id,
                               'Введенный адрес не является корпоративной почтой НИУ ВШЭ. Введите корректный адрес.')
        bot.register_next_step_handler(msg, check_email)
    else:
        schedule = ruz.person_lessons(mail)
        if schedule:
            msg = bot.send_message(message.chat.id,
                                   'Получаю данные...')
            bot.register_next_step_handler(msg, get_schedule)
        else:
            msg = bot.send_message(message.chat.id,
                                   'Для этого адреса расписание отсутствует. Возможно, вы ошиблись. Проверьте правильность написания и отправьте мне корректный адрес.')
            bot.register_next_step_handler(msg, check_email)


def get_schedule(message):
    global schedule
    print(schedule)
    auditorium = schedule[0]['auditorium']
    print(auditorium)
    bot.send_message(message.chat.id,
                     auditorium)


# На этом моменте происходит ошибка ERROR - TeleBot: "A request to the Telegram API was unsuccessful. Error code: 403. Description: Forbidden: USER_BOT_INVALID"


@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    # Если сообщение из чата с ботом
    if call.data == "professor":
        results = []
        action_string = 'typing'
        bot.send_chat_action(call.message.chat.id, action_string)

        msg = bot.send_message(call.message.chat.id, 'Напиши мне имя своего преподавателя, пожалуйста')
        results.append(msg)
        bot.answer_inline_query(call.id, results)
        # НАПИШИ ТУТ ФУНКЦИЮ ПОИСКА ПРЕПОДАВАТЕЛЕЙ

    if call.data == 'freshman' or call.data == 'second_year' or call.data == 'third_year' or call.data == 'forth_year':
        results = []
        msg = bot.send_message(call.message.chat.id, 'Какой предмет ты хочешь оценить?')
        results.append(msg)
        bot.answer_inline_query(call.id, results)
        any_msg()


def main():
    print('launching...')


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        exit()
    bot.polling(none_stop=True, interval=0)
