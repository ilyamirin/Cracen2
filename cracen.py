import os
from hashlib import md5
import telebot
import logging
import yaml
import re


def hide_password(password: str) -> str:
    return password[0] + ''.join(list(map(lambda c: '*', password[1:-1]))) + password[-1]


logging.basicConfig(filename="bot.log", level=logging.INFO, format='%(asctime)s  %(name)s  %(levelname)s: %(message)s')
log = open('queries.log', 'a')

config = {}
with open("config.yml", 'r') as stream:
    config = yaml.safe_load(stream)

bot = telebot.TeleBot(config['token'])


def find_passwords(db_path: str, email: str) -> list:
    h = md5(email.encode('utf-8')).hexdigest()[:5]
    result = list()
    if not os.path.exists(db_path + h):
        return result
    else:
        f = open(db_path + h, "r")
        for line in f.readlines():
            if line[0] > email[0]:
                break
            if line.startswith(email) > 0:
                result.append(line.split(';')[1])
        f.close()
    return result


@bot.message_handler(commands=['start', 'help'])
def start(message):
    try:
        bot.send_message(message.chat.id, 'Скажи мне волшебное слово, %s' % message.chat.username)
    except Exception as e:
        logging.error('Error while sending /help', exc_info=e)


@bot.message_handler(content_types=['text'])
def get_text_messages(message):
    try:
        m = re.search(r"(^[a-zA-ZА-я0-9_.+-]+@[a-zA-ZА-я0-9-]+\.[a-zA-ZА-я0-9-.]+$)", str(message.text).strip())
        if m:
            passwords = find_passwords('data' + os.sep, m.group())
            if len(passwords) > 0:
                for password in passwords:
                    bot.send_message(message.from_user.id, hide_password(password))
            else:
                bot.send_message(message.from_user.id, "Этого нет в моей базе утечек.")
        else:
            bot.send_message(message.from_user.id, "Этот текст \"%s\" не похож на волшебное слово." % message.text)
    except Exception as e:
        logging.error('Error while sending text', exc_info=e)


bot.polling()
