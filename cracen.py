import telebot
import logging
import yaml
from pymongo import MongoClient
import re


def hide_password(password: str) -> str:
    return password[0] + ''.join(list(map(lambda c: '*', password[1:-1]))) + password[-1]


logging.basicConfig(filename="bot.log", level=logging.INFO, format='%(asctime)s  %(name)s  %(levelname)s: %(message)s')
log = open('queries.log', 'a')

config = {}
with open("config.yml", 'r') as stream:
    config = yaml.safe_load(stream)

client = MongoClient(config['mongodb'])
db = client.cracen
email_leaks_collection = db.email_leaks_collection

bot = telebot.TeleBot(config['token'])


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
            email = email_leaks_collection.find_one({'email': m.group()})
            if email is not None:#emails.count() > 0:
                #for email in emails:
                bot.send_message(message.from_user.id, hide_password(email['password']))
            else:
                bot.send_message(message.from_user.id, "Этой почты нет в моей базе утечек")
        else:
            bot.send_message(message.from_user.id, "Этот текст \"{%s}\" не похож на электронную почту." % message.text)
    except Exception as e:
        logging.error('Error while sending text', exc_info=e)


bot.polling()
