import telebot
from telebot import types
import ruz
import re
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
import smtplib, ssl
from email import encoders 

token = '1491361372:AAFYb8HoCGoC_QAE8NPHhdktao7OtMySZLo'
bot = telebot.TeleBot(token)

global schedule
global filename


@bot.message_handler(commands=['start'])
def starting(message):
    email = bot.send_message(message.chat.id,
                             "Привет! Я люблю собирать обратную связь, это моя работа. Пожалуйста, напишите свой адрес корпоративной почты.")
    bot.register_next_step_handler(email, check_email)


@bot.message_handler(content_types=["text"])
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
            get_schedule(message)
        else:
            msg = bot.send_message(message.chat.id,
                                   'Для этого адреса расписание отсутствует. Возможно, вы ошиблись. Проверьте правильность написания и отправьте мне корректный адрес.')
            bot.register_next_step_handler(msg, check_email)


def get_schedule(message):
    global schedule
    years = []
    months = []
    days = []
    hours = []
    minutes = []
    for i in range(len(schedule)):
        lecture_date = schedule[i]['date']
        lecture_time = schedule[i]['beginLesson']
        lect_date = lecture_date.split('.')
        lect_time = lecture_time.split(':')
        years.append(int(lect_date[0]))
        months.append(int(lect_date[1]))
        days.append(int(lect_date[2]))
        hours.append(int(lect_time[0]))
        minutes.append(int(lect_time[1]))
    for i in range(len(schedule)):
        global filename
        # print(str(years[i]) + '.' + str(months[i]) + '.' + str(days[i]) + ' ' + str(hours[i]) + ':' + str(minutes[i]))
        filename = str(schedule[i]['discipline']) + ' ' + str(schedule[i]['lecturer']) + ' ' + str(schedule[i]['date'])
        scheduler = BackgroundScheduler()
        scheduler.start()
        scheduler.add_job(get_feedback, 'date',
                          run_date=datetime(years[i], months[i], days[i], hours[i], minutes[i], 00), args=[message])


def get_feedback(message):
    keyboard = types.InlineKeyboardMarkup()
    callback_1 = types.InlineKeyboardButton(text="1", callback_data="1")
    callback_2 = types.InlineKeyboardButton(text="2", callback_data="2")
    callback_3 = types.InlineKeyboardButton(text="3", callback_data="3")
    callback_4 = types.InlineKeyboardButton(text="4", callback_data="4")
    callback_5 = types.InlineKeyboardButton(text="5", callback_data="5")
    keyboard.add(callback_1, callback_2, callback_3, callback_4, callback_5)

    bot.send_message(message.chat.id, 'Как ты оцениваешь это занятие? Пожалуйста, оцени по шкале от 1 до 5.',
                     reply_markup=keyboard)
    msg = bot.send_message(message.chat.id,
                           'Напиши комментарии, замечания или жалобы относительно этого занятия. Если не хочешь оставлять отзыв, просто напиши "нет".')
    bot.register_next_step_handler(msg, get_opinion)


def get_opinion(message):
    global schedule
    global filename
    if message.text.lower() != 'нет':
        with open(filename + 'opinions.txt', 'a', encoding='utf-8') as f:
            f.write(message.text + '\n')
        years = []
        months = []
        days = []
        for i in range(len(schedule)):
            scheduler = BackgroundScheduler()
            scheduler.start()
            lecture_date = schedule[i]['date']
            lect_date = lecture_date.split('.')
            years.append(int(lect_date[0]))
            months.append(int(lect_date[1]))
            days.append(int(lect_date[2]))
            scheduler.add_job(search_professor, 'date', run_date=datetime(years[i], months[i], days[i], 23, 30, 00),
                              args=[])
            bot.send_message(message.chat.id, 'Спасибо!')
    else:
        bot.send_message(message.chat.id, 'Хорошо, спасибо. До встречи!')


def search_professor():
    global schedule
    email = schedule[0]['lecturerEmail']
    port = 587
    smtp_server = 'smtp.gmail.com'
    sender_email = 'fdsffgshgh@gmail.com'
    password = '***'
    receiver_email = email
    subject = 'Оценка пар за неделю'
    with open('opinion_results.txt', encoding='utf-8') as fp:
        a = fp.read()
        message = 'Subject: {}\n\n{}'.format(subject, a).encode('utf-8')
        context = ssl.create_default_context()
        with smtplib.SMTP(smtp_server, port) as server:
            server.ehlo()
            server.starttls(context=context)
            server.ehlo()
            server.login(sender_email, password)
            server.sendmail(sender_email, receiver_email, message)


@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    global filename
    with open(filename + 'marks.txt', 'a', encoding='utf-8') as f:
        if call.data == '1':
            f.write('1 ')
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                  text="Спасибо за оценку!")
        if call.data == '2':
            f.write('2 ')
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                  text="Принято!")
        if call.data == '3':
            f.write('3 ')
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="Понял!")
        if call.data == '4':
            f.write('4 ')
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="Супер!")
        if call.data == '5':
            f.write('5 ')
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="Ого!")


def main():
    print('launching...')


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        exit()
    bot.polling(none_stop=True, interval=0)
