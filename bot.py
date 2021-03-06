import telebot
import time

TOKEN = '1684905058:AAFSLUrt-U0GZaHs3YrCBcVajsSYX7Pohsc'
tb = telebot.TeleBot(TOKEN) #create a new Telegram Bot object

# TeleBot will not create thread for message listener. Default is True.
tb = telebot.TeleBot(TOKEN, False)

# 4 Thread worker for message listener.
tb = telebot.TeleBot(TOKEN, True, 4)

# Setup telebot handler to telebot logger. If you want to get some information from telebot.
# More information at Logging section
handler = logging.StreamHandler(sys.stdout)
telebot.logger.addHandler(handler)
telebot.logger.setLevel(logging.INFO)

# getMe
user = tb.get_me()

# sendMessage
tb.send_message(chatid, text)

# forwardMessage
# tb.forward_message(10894,926,3)
tb.forward_message(to_chat_id, from_chat_id, message_id)

# sendPhoto
photo = open('/tmp/photo.png', 'rb')
tb.send_photo(chat_id, photo)
file_id = 'AAAaaaZZZzzz'
tb.send_photo(chat_id, file_id)

# sendAudio
audio = open('/tmp/audio.ogg', 'rb')
tb.send_audio(chat_id, audio)
file_id = 'AAAaaaZZZzzz'
tb.send_audio(chat_id, file_id)

# sendDocument
doc = open('/tmp/file.txt', 'rb')
tb.send_document(chat_id, doc)
file_id = 'AAAaaaZZZzzz'
tb.send_document(chat_id, file_id)

# sendSticker
sti = open('/tmp/sti.webp', 'rb')
tb.send_sticker(chat_id, sti)
file_id = 'AAAaaaZZZzzz'
tb.send_sticker(chat_id, file_id)

# sendVideo
video = open('/tmp/video.mp4', 'rb')
tb.send_video(chat_id, video)
file_id = 'AAAaaaZZZzzz'
tb.send_video(chat_id, file_id)

# sendLocation
tb.send_location(chat_id, lat, lon)

# sendChatAction
# action_string can be one of the following strings: 'typing', 'upload_photo', 'record_video', 'upload_video',
# 'record_audio', 'upload_audio', 'upload_document' or 'find_location'.
tb.send_chat_action(chat_id, action_string)

# Use the ReplyKeyboardMarkup class.
# Thanks pevdh.
from telebot import types

markup = types.ReplyKeyboardMarkup()
markup.add('a', 'v', 'd')
tb.send_message(chat_id, message, reply_markup=markup)

# or add strings one row at a time:
markup = types.ReplyKeyboardMarkup()
markup.row('a', 'v')
markup.row('c', 'd', 'e')
tb.send_message(chat_id, message, reply_markup=markup)