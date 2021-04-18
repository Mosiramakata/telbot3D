import telebot
from telebot import types
import alpaca_trade_api as tradeip

# from main import *

interval = 3
key = ''
secret_key = ''
alp = None

token = '1684905058:AAFSLUrt-U0GZaHs3YrCBcVajsSYX7Pohsc'
bot = telebot.TeleBot(token)
main_markup = types.ReplyKeyboardMarkup(row_width=1)
start_markup = types.ReplyKeyboardMarkup(row_width=1)

shares_movenment_button = types.KeyboardButton('Изменение акций')
time_interval_button = types.KeyboardButton('Ввести временной интервал')
account_button = types.KeyboardButton('Ввести данные аккаунта')
buy_button = types.KeyboardButton('Купить акции')

main_markup.add(shares_movenment_button, time_interval_button, buy_button, account_button)
start_markup.add(account_button)


# Mokata:
#   key = 'PK1LTOY8SGXG325T26D0'
#   secret_key = 'fnPEzhro2BoChsnqwW2bWaN6Lv4w8EnBLCv7QjCK'

# Brom:
#   key = 'PK1FLFQHG1UFHPEY69SR'
#   secret_key = 'mFBb5BDpo2jkuxHhB4IA4jCkrIrZuMLwWPVY5ntY'

class Alpaca(object):
    def __init__(self, key, secret):
        self.key = key
        self.secret = secret
        self.alpaca_endpoint = 'https://paper-api.alpaca.markets'
        self.api = tradeip.REST(self.key, self.secret, self.alpaca_endpoint)
        self.symbol = 'IVV'
        self.current_order = None
        self.last_price = 1

        try:
            self.position = int(self.api.get_position(self.symbol).qty)
        except:
            self.position = 0

    def submit_order(self, target):
        if self.current_order is not None:
            self.api.cancel_order(self.current_order.id)

        delta = target - self.position
        if delta == 0:
            return
        print(f'Proccessing the order for {target} shares')

        if delta > 0:
            buy_quantity = delta
            if self.position < 0:
                buy_quantity = min(abs(self.position), buy_quantity)
            print(f'Buying {buy_quantity} shares')
            self.current_order = self.api.submit_order(self.symbol, buy_quantity, 'buy', 'limit', 'day',
                                                       self.last_price)

        elif delta < 0:
            sell_quantity = delta
            if self.position > 0:
                sell_quantity = min(abs(self.position), sell_quantity)
            print(f'Selling {sell_quantity} shares')
            self.current_order = self.api.submit_order(self.symbol, sell_quantity, 'sell', 'limit', 'day',
                                                       self.last_price)


def main():
    pass
    # alpaca_main()


def alpaca_main():
    check_balance()
    check_market()
    share_movenment()


def check_balance():
    account = alp.api.get_account()
    # Check our current balance vs. our balance at the last market close
    balance_change = float(account.equity) - float(account.last_equity)
    print(f'Today\'s portfolio balance change: ${balance_change}')

    aapl_asset = alp.api.get_asset('AAPL')
    if aapl_asset.tradable:
        print('We can trade AAPL.')

    # active_assets = alp.api.list_assets(status='active')
    #
    # Filter the assets down to just those on NASDAQ.
    # nasdaq_assets = [a for a in active_assets if a.exchange == 'NASDAQ']
    # print(nasdaq_assets)


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


def share_movenment(message=None):
    barset = alp.api.get_barset('VVI', 'day', limit=interval)
    aapl_bars = barset['VVI']
    # f1 = open('doc_from_main.txt', 'w')
    # See how much AAPL moved in that timeframe.
    week_open = aapl_bars[0].o
    week_close = aapl_bars[-1].c
    percent_change = (week_close - week_open) / week_open * 100
    print('VVI moved ' + str(percent_change) + '% over the last ' + str(interval) + ' days')  # .format(percent_change))
    if message != None:
        bot.send_message(message.chat.id, 'VVI moved ' + str(percent_change) + '% over the last ' + str(interval) + ' days')


def set_time_interval(message):
    if message.text.isdigit() == False:
        bot.send_message(message.chat.id, 'Ошибка ввода, попробуйте ещё раз')
        return
    global interval
    interval = int(message.text)
    bot.send_message(message.chat.id, 'Временной интервал: ' + message.text)


def input_account_information(message):
    global alp
    key = message.text.split()[0]
    secret_key = message.text.split()[1]
    alp = Alpaca(key, secret_key)
    bot.send_message(message.chat.id, 'Данные аккаунта введены', reply_markup=main_markup)


def buy_shares(message):
    if message.text.isdigit() == False:
        bot.send_message(message.chat.id, 'Ошибка ввода, попробуйте ещё раз')
        return
    alp.submit_order(int(message.text))
    bot.send_message(message.chat.id, 'Совершена покупка акций в количестве ' + message.text)


@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.send_message(message.chat.id,
                     "Добро пожаловать, {0.first_name}! \nЯ - {1.first_name}, бот, который автотрейдер pog.".format(
                         message.from_user, bot.get_me()), reply_markup=start_markup)


@bot.message_handler(content_types=['text'])
def read_action_change(message):
    if message.chat.type == 'private':
        if message.text == 'Изменение акций' and alp != None:
            share_movenment(message)
        elif message.text == 'Ввести временной интервал' and alp != None:
            send = bot.send_message(message.chat.id, 'Введите временной интервал')
            bot.register_next_step_handler(send, set_time_interval)
        elif message.text == 'Ввести данные аккаунта':
            send = bot.send_message(message.chat.id, 'Введите ключ и секретный ключ')
            bot.register_next_step_handler(send, input_account_information)
        elif message.text == 'Купить акции':
            send = bot.send_message(message.chat.id, 'Введите количество акций')
            bot.register_next_step_handler(send, buy_shares)

        # else:
        #    bot.send_message(message.chat.id, 'Некоректный ввод, повторите попытку')


bot.polling()

if __name__ == '__main__':
    main()
