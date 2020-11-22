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
    email = bot.send_message(message.chat.id, "Hi! My job is to collect student feedback. Please tell me your student e-mail (should end with @edu.hse.ru).")
    bot.register_next_step_handler(email, check_email)


@bot.message_handler(content_types=["text"])
def check_email(message):
    global schedule
    pttrn = ",\s'text':\s'([^']+)"
    mail = re.findall(pttrn, str(message))[0]
    check = ruz.utils.is_valid_hse_email(mail)
    print(mail)
    print(check)
    if not check:
        msg = bot.send_message(message.chat.id,
                               'This address is incorrect. Please enter a valid HSE e-mail.')
        bot.register_next_step_handler(msg, check_email)
    else:
        schedule = ruz.person_lessons(mail)
        if schedule:
            bot.send_message(message.chat.id, "Thank you! I'll talk to you later.")
            get_schedule(message)
        else:
            msg = bot.send_message(message.chat.id,
                                   'Could not find the schedule for this e-mail address. Please check your spelling and try again.')
            bot.register_next_step_handler(msg, check_email)


def get_schedule(message):
    global schedule
    # years = []
    # months = []
    # days = []
    # hours = []
    # minutes = []
    # for i in range(len(schedule)):
    #     lecture_date = schedule[i]['date']
    #     lecture_time = schedule[i]['beginLesson']
    #     lect_date = lecture_date.split('.')
    #     lect_time = lecture_time.split(':')
    #     years.append(int(lect_date[0]))
    #     months.append(int(lect_date[1]))
    #     days.append(int(lect_date[2]))
    #     hours.append(int(lect_time[0]))
    #     minutes.append(int(lect_time[1]))
    # for i in range(len(schedule)):
    #     global filename
    #     # print(str(years[i]) + '.' + str(months[i]) + '.' + str(days[i]) + ' ' + str(hours[i]) + ':' + str(minutes[i]))
    #     filename = str(schedule[i]['discipline']) + ' ' + str(schedule[i]['lecturer']) + ' ' + str(schedule[i]['date'])
    #     scheduler = BackgroundScheduler()
    #     scheduler.start()
    #     scheduler.add_job(get_feedback, 'date',
    #                       run_date=datetime(years[i], months[i], days[i], hours[i], minutes[i], 00), args=[message])
    global filename
    filename = str(schedule[0]['discipline']) + ' ' + str(schedule[0]['lecturer']) + ' ' + str(schedule[0]['date'])
    scheduler = BackgroundScheduler()
    scheduler.start()
    scheduler.add_job(get_feedback, 'date', run_date=datetime(2020, 11, 22, 14, 6, 20), args=[message])


def get_feedback(message):
    keyboard = types.InlineKeyboardMarkup()
    callback_1 = types.InlineKeyboardButton(text="1", callback_data="1")
    callback_2 = types.InlineKeyboardButton(text="2", callback_data="2")
    callback_3 = types.InlineKeyboardButton(text="3", callback_data="3")
    callback_4 = types.InlineKeyboardButton(text="4", callback_data="4")
    callback_5 = types.InlineKeyboardButton(text="5", callback_data="5")
    keyboard.add(callback_1, callback_2, callback_3, callback_4, callback_5)

    bot.send_message(message.chat.id, 'Please rate this class on a scale from 1 to 5.',
                     reply_markup=keyboard)
    msg = bot.send_message(message.chat.id,
                           'Take a minute to tell us what you think about the class. You can tell us what was unclear or something you enjoyed. If you do not want to provide feedback, please write "no".')
    bot.register_next_step_handler(msg, get_opinion)


def get_opinion(message):
    global schedule
    global filename
    if message.text.lower() != 'no':
        with open(filename + 'opinions.txt', 'a', encoding='utf-8') as f:
            f.write(message.text + '\n')
        # years = []
        # months = []
        # days = []
        # for i in range(len(schedule)):
        #     scheduler = BackgroundScheduler()
        #     scheduler.start()
        #     lecture_date = schedule[i]['date']
        #     lect_date = lecture_date.split('.')
        #     years.append(int(lect_date[0]))
        #     months.append(int(lect_date[1]))
        #     days.append(int(lect_date[2]))
        #     scheduler.add_job(search_professor, 'date', run_date=datetime(years[i], months[i], days[i], 23, 30, 00),
        #                       args=[])
        #     bot.send_message(message.chat.id, 'Thank you!')
        scheduler = BackgroundScheduler()
        scheduler.start()
        scheduler.add_job(search_professor, 'date', run_date=datetime(2020, 11, 22, 14, 6, 50), args=[])
        bot.send_message(message.chat.id, 'Thank you!')
    else:
        bot.send_message(message.chat.id, 'See you soon!')


def search_professor():
    global schedule
    with open(filename + 'marks.txt', 'r', encoding='utf-8') as marks:
        mark = marks.read()
        all_marks = mark.split(' ')
        all_marks = [int(m) for m in all_marks if m]
        avg_mark = sum(all_marks) / len(all_marks)
    # email = schedule[0]['lecturerEmail']
    with open(filename + 'opinions.txt', 'a', encoding='utf-8') as op:
        op.write('Average student mark: ' + str(avg_mark) + '\n')
    port = 587
    smtp_server = 'smtp.gmail.com'
    sender_email = 'fdsffgshgh@gmail.com'
    password = 'Qwertyuioppp123'
    receiver_email = 'ra4wv2@gmail.com'
    subject = "Today's evaluation"
    with open(filename + 'opinions.txt', encoding='utf-8') as fp:
        a = fp.read() + '\n\nRespectfully,\nYour favourite bot'
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
                                  text="Thank you!")
        if call.data == '2':
            f.write('2 ')
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                  text="Thank you!")
        if call.data == '3':
            f.write('3 ')
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="Thank you!")
        if call.data == '4':
            f.write('4 ')
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="Thank you!")
        if call.data == '5':
            f.write('5 ')
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="Thank you!")


def main():
    print('launching...')


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        exit()
    bot.polling(none_stop=True, interval=0)
