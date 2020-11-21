import telebot
from telebot import types
import os


token = os.environ['TOKEN']
bot = telebot.TeleBot(token)

@bot.message_handler(commands=['start'])
def starting(message):
    bot.send_message(message.chat.id, "Привет! Я люблю собирать обратную связь, это моя работа.")
    ask_course(message)

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

def ask_course(message):
    keyboard = types.InlineKeyboardMarkup()
    first_year = types.InlineKeyboardButton(text="1", callback_data="freshman")
    second_year = types.InlineKeyboardButton(text="2", callback_data="second_year")
    third_year = types.InlineKeyboardButton(text="3", callback_data="third_year")
    forth_year = types.InlineKeyboardButton(text="4", callback_data="forth_year")
    keyboard.add(first_year, second_year, third_year, forth_year)
    bot.send_message(message.chat.id, 'Для начала скажи мне, на каком ты курсе?', reply_markup=keyboard)

@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    if call.data == "professor":
        results = []
        action_string = 'typing'
        bot.send_chat_action(call.message.chat.id, action_string)
        msg = bot.send_message(call.message.chat.id, 'Напиши мне имя своего преподавателя, пожалуйста')
        results.append(msg)
        bot.answer_inline_query(call.id, results)

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