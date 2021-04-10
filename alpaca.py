import alpaca_trade_api as tradeip


class Alpaca(object):
    def __init__(self):
        self.key = 'PK1LTOY8SGXG325T26D0'
        self.secret = 'fnPEzhro2BoChsnqwW2bWaN6Lv4w8EnBLCv7QjCK'
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
            self.current_order = self.api.submit_order(self.symbol, buy_quantity, 'buy', 'limit', 'day', self.last_price)

        elif delta < 0:
            sell_quantity = delta
            if self.position > 0:
                sell_quantity = min(abs(self.position), sell_quantity)
            print(f'Selling {sell_quantity} shares')
            self.current_order = self.api.submit_order(self.symbol, sell_quantity, 'sell', 'limit', 'day', self.last_price)

if __name__ == '__main__':
    alp = Alpaca()
    alp.submit_order(3)

    account = alp.api.get_account()
    # Check our current balance vs. our balance at the last market close
    balance_change = float(account.equity) - float(account.last_equity)
    print(f'Today\'s portfolio balance change: ${balance_change}')

    aapl_asset = alp.api.get_asset('AAPL')
    if aapl_asset.tradable:
        print('We can trade AAPL.')

    # active_assets = alp.api.list_assets(status='active')
    #
    # # Filter the assets down to just those on NASDAQ.
    # nasdaq_assets = [a for a in active_assets if a.exchange == 'NASDAQ']
    # print(nasdaq_assets)

    clock = alp.api.get_clock()
    print('The market is {}'.format('open.' if clock.is_open else 'closed.'))

    # Check when the market was open on Dec. 1, 2018
    date = '2021-04-08'
    calendar = alp.api.get_calendar(start=date, end=date)[0]
    print('The market opened at {} and closed at {} on {}.'.format(
        calendar.open,
        calendar.close,
        date
    ))

    barset = alp.api.get_barset('VVI', 'day', limit=5)
    aapl_bars = barset['VVI']

    # See how much AAPL moved in that timeframe.
    week_open = aapl_bars[0].o
    week_close = aapl_bars[-1].c
    percent_change = (week_close - week_open) / week_open * 100
    print('VVI moved {}% over the last 5 days'.format(percent_change))
