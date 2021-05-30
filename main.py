import telebot
from telebot import types
import alpaca_trade_api as tradeip
import time


# from main import *

interval = 3
key = ''
secret_key = ''
alp = None

token = '1684905058:AAENIhHYwE1qVjIqWAFjSEMvLJtMxlJO1dg'
bot = telebot.TeleBot(token)
main_markup = types.ReplyKeyboardMarkup(row_width=1)
start_markup = types.ReplyKeyboardMarkup(row_width=1)
accounts = dict()

check_market_button = types.KeyboardButton('Проверить работоспособность рынка')
shares_movenment_button = types.KeyboardButton('Изменение акций')
account_button = types.KeyboardButton('Изменить данные аккаунта')
buy_button = types.KeyboardButton('Купить акции')
sell_button = types.KeyboardButton('Продать акции')

main_markup.add(check_market_button, shares_movenment_button, buy_button, sell_button, account_button)


# Mokata:
#   key = 'PK1LTOY8SGXG325T26D0'
#   secret_key = 'fnPEzhro2BoChsnqwW2bWaN6Lv4w8EnBLCv7QjCK'

# Brom:
#   key = 'PK0FYUD4HCLQSH46T79L'
#   secret_key = 'r7mGbmDLRs6MuNTARZVhr9tsv8jUf4L65rIwYFv6'

class Alpaca(object):
    def __init__(self, key, secret):
        self.key = key
        self.secret = secret
        self.alpaca_endpoint = 'https://paper-api.alpaca.markets'
        self.api = tradeip.REST(base_url=self.alpaca_endpoint, key_id=self.key, secret_key=self.secret)
        self.symbol = 'IVV'
        # self.current_order = None
        # self.last_price = 1
        self.time_interval = 1

        try:
            self.position = int(self.api.get_position(self.symbol).qty)
        except:
            self.position = 0

    def set_symbol(self, symbol):
        self.symbol = symbol

    def submit_order(self, target, act):
        # if self.current_order is not None:
        #    self.api.cancel_order(self.current_order.id)

        # symbol_bars = self.api.get_barset(self.symbol, 'minute', 1).df.iloc[0]
        # symbol_price = symbol_bars[self.symbol]['close']

        self.api.submit_order(
            symbol=self.symbol,
            qty=target,
            side=act,
            type='market',
            time_in_force='gtc'
            # ,
            # order_class='bracket',
            # stop_loss={'stop_price': symbol_price * 0.95,
            #            'limit_price': symbol_price * 0.94},
            # take_profit={'limit_price': symbol_price * 1.05}
        )

    def set_key_secret(self, key, secret_key):
        self.key = key
        self.secret = secret_key
        self.api = tradeip.REST(base_url=self.alpaca_endpoint, key_id=self.key, secret_key=self.secret)


def listener(messages):
    for m in messages:
        print(m.chat.id)
        return int(m.chat.id)


def check_balance(message):
    alp.set_key_secret(accounts[message.chat.id][0],accounts[message.chat.id][1])
    account = alp.api.get_account()
    # Check our current balance vs. our balance at the last market close
    balance_change = float(account.equity) - float(account.last_equity)
    print(f'Today\'s portfolio balance change: ${balance_change}')


def check_tradability(symbol='TON'):
    aapl_asset = alp.api.get_asset(symbol)
    if aapl_asset.tradable:
        return True
    else:
        return False


def check_available_tradesymbols(message):
    symbol = message.text
    active_assets = alp.api.list_assets(status='active')
    symbol_assets = [a for a in active_assets if a.exchange == symbol]
    # bot.send_message(message.chat.id, symbol_assets)


def check_market():
    clock = alp.api.get_clock()
    print('The market is {}'.format('open.' if clock.is_open else 'closed.'))

    # Check when the market was open
    date = '2021-04-11'
    calendar = alp.api.get_calendar(start=date, end=date)[0]
    print('The market opened at {} and closed at {} on {}.'.format(
        calendar.open,
        calendar.close,
        date
    ))


def set_time_interval(message):
    if message.text.isdigit() == False:
        bot.send_message(message.chat.id, 'Ошибка ввода, попробуйте ещё раз')
        return
    global alp
    alp.time_interval = int(message.text)
    send = bot.send_message(message.chat.id, 'Введите название акции')
    bot.register_next_step_handler(send, share_movenment)


def share_movenment(message):
    global alp
    alp.set_key_secret(accounts[message.chat.id][0], accounts[message.chat.id][1])
    check = 0
    txt = message.text.upper()
    active_assets = alp.api.list_assets(status='active')
    for i in active_assets:
        if i.symbol == txt:
            check = 1
    if check == 0:
        bot.send_message(message.chat.id, 'Ошибка ввода, попробуйте ещё раз')
        return
    if not check_tradability(txt):
        bot.send_message(message.chat.id, 'Невозможно трейдить данные акции, попробуйте ещё раз')
        return
    else:
        alp.set_symbol(txt)
    barset = alp.api.get_barset(alp.symbol, 'day', limit=alp.time_interval)
    aapl_bars = barset[alp.symbol]
    # f1 = open('doc_from_main.txt', 'w')
    # See how much AAPL moved in that timeframe.
    week_open = aapl_bars[0].o
    week_close = aapl_bars[-1].c
    percent_change = (week_close - week_open) / week_open * 100
    print(alp.symbol + ' moved ' + str(percent_change) + '% over the last ' + str(
        alp.time_interval) + ' days')  # .format(percent_change))
    bot.send_message(message.chat.id,
                     alp.symbol + ' moved ' + str(percent_change) + '% over the last ' + str(alp.time_interval) + ' days')


def input_account_information(message):
    global alp
    key = message.text.split()[0]
    secret_key = message.text.split()[1]
    accounts.setdefault(message.chat.id, [key, secret_key])
    alp = Alpaca(key, secret_key)
    bot.send_message(message.chat.id, 'Данные аккаунта введены', reply_markup=main_markup)


def check_shares_for_sale_symbol(message):
    global alp
    alp.set_key_secret(accounts[message.chat.id][0], accounts[message.chat.id][1])
    check = 0
    txt = message.text.upper()
    active_assets = alp.api.list_assets(status='active')
    for i in active_assets:
        if i.symbol == txt:
            check = 1
    if check == 0:
        bot.send_message(message.chat.id, 'Ошибка ввода, попробуйте ещё раз')
        return
    if not check_tradability(txt):
        bot.send_message(message.chat.id, 'Невозможно трейдить данные акции, попробуйте ещё раз')
        return
    else:
        alp.set_symbol(txt)
        send = bot.send_message(message.chat.id, 'Введите колличество акций для покупки')
        bot.register_next_step_handler(send, buy_shares)


def buy_shares(message):
    alp.set_key_secret(accounts[message.chat.id][0], accounts[message.chat.id][1])
    amount = message.text
    if amount.isdigit() == False:
        bot.send_message(message.chat.id, 'Ошибка ввода, попробуйте ещё раз')
        return
    alp.submit_order(int(message.text), 'buy')
    bot.send_message(message.chat.id, 'Совершена покупка акций ' + alp.symbol + ' в количестве ' + message.text)


def check_shares_to_buy_symbol(message):
    global alp
    alp.set_key_secret(accounts[message.chat.id][0], accounts[message.chat.id][1])
    check = 0
    txt = message.text.upper()
    active_assets = alp.api.list_assets(status='active')
    for i in active_assets:
        if i.symbol == txt:
            check = 1
    if check == 0:
        bot.send_message(message.chat.id, 'Ошибка ввода, попробуйте ещё раз')
        return
    if not check_tradability(txt):
        bot.send_message(message.chat.id, 'Невозможно трейдить данные акции, попробуйте ещё раз')
        return
    else:
        alp.set_symbol(txt)
        send = bot.send_message(message.chat.id, 'Введите колличество акций для продажи')
        bot.register_next_step_handler(send, sell_shares)


def sell_shares(message):
    alp.set_key_secret(accounts[message.chat.id][0], accounts[message.chat.id][1])
    amount = message.text
    if amount.isdigit() == False:
        bot.send_message(message.chat.id, 'Ошибка ввода, попробуйте ещё раз')
        return
    alp.submit_order(int(message.text), 'sell')
    bot.send_message(message.chat.id, 'Совершена продажа акций ' + alp.symbol + ' в количестве ' + message.text)


@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.send_message(message.chat.id,
                     "Добро пожаловать, {0.first_name}! \nЯ - {1.first_name}, бот, который автотрейдер pog.".format(
                         message.from_user, bot.get_me()), reply_markup=start_markup)
    send = bot.send_message(message.chat.id, 'Введите ключ и секретный ключ')
    bot.register_next_step_handler(send, input_account_information)


@bot.message_handler(content_types=['text'])
def read_action_change(message):
    if message.chat.type == 'private':
        if message.text == 'Проверить работоспособность рынка' and alp != None:
            clock = alp.api.get_clock()
            bot.send_message(message.chat.id, 'The market is {}'.format('open.' if clock.is_open else 'closed.'))
        elif message.text == 'Изменение акций' and alp != None:
            send = bot.send_message(message.chat.id, 'Введите временной интервал')
            bot.register_next_step_handler(send, set_time_interval)
        elif message.text == 'Изменить данные аккаунта':
            send = bot.send_message(message.chat.id, 'Введите ключ и секретный ключ')
            bot.register_next_step_handler(send, input_account_information)
        elif message.text == 'Купить акции' and alp != None:
            send = bot.send_message(message.chat.id, 'Введите название акции')
            bot.register_next_step_handler(send, check_shares_for_sale_symbol)
        elif message.text == 'Продать акции' and alp != None:
            send = bot.send_message(message.chat.id, 'Введите название акции')
            bot.register_next_step_handler(send, check_shares_to_buy_symbol)


while True:
    try:
        bot.polling(none_stop=True)

    except Exception as e:
        print(e)  # или просто print(e) если у вас логгера нет,
        # или import traceback; traceback.print_exc() для печати полной инфы
        time.sleep(15)

