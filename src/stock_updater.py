import datetime
import pytz
import holidays
import yfinance as yf

from time import sleep
from threading import Thread
from logger import Logger
from influxdb_client import TickerType
log = Logger.getInstance().getLogger()

TIMER_SLEEP_MIN = (5 * 60)
MARKET_CLOSE_SLEEP = (30 * 60)
RATE_LIMIT_REQUEST = (10)
TIME_ZONE = pytz.timezone('US/Pacific')
US_HOLIDAYS = holidays.US()


class StockStats(Thread):

    def __init__(self, tickers, influxdb_clients=None, timer=TIMER_SLEEP_MIN):
        Thread.__init__(self)
        self.setDaemon(True)
        self.tickers = tickers
        self.influxdb_clients = influxdb_clients
        self.timer = timer

    def is_market_close(self, now=None):
        if not now:
            now = datetime.datetime.now(TIME_ZONE)
        open_time = datetime.time(hour=6, minute=30, second=0)
        close_time = datetime.time(hour=13, minute=0, second=0)

        # If its a holiday
        if now.strftime('%Y-%m-%d') in US_HOLIDAYS:
            return True

        # If before 06:30 or after 16:00
        if (now.time() < open_time) or (now.time() > close_time):
            return True

        # If its the weekend
        if now.date().weekday() > 4:
            return True

        return False

    def update_crypto_coins(self):
        if self.influxdb_clients:
            for name, db_client in self.influxdb_clients.items():
                if db_client.get_type() != TickerType.CRYPTO:
                    continue
                log.info("Updating {}".format(name))
                ticker = yf.Ticker(name)
                history = ticker.history()
                last_quote = (history.tail(1)['Close'].iloc[0])
                # data = ("Price={:0.2f}").format(last_quote)
                data = ("Price={}").format(last_quote)
                # log.info(data)
                db_client.write_data(data=data)
                sleep(RATE_LIMIT_REQUEST)

    def run(self):
        while True:
            if self.is_market_close():
                # Crypto never sleeps!
                self.update_crypto_coins()
                sleep(TIMER_SLEEP_MIN)
                continue

            try:
                if self.influxdb_clients:
                    # Inject to InfluxDB
                    for name, db_client in self.influxdb_clients.items():
                        ticker = yf.Ticker(name)
                        history = ticker.history()
                        last_quote = (history.tail(1)['Close'].iloc[0])
                        data = 0
                        if db_client.get_type() != TickerType.CRYPTO:
                            data = ("Price={:0.2f}").format(last_quote)
                        else:
                            data = ("Price={}").format(last_quote)
                        # log.info(data)
                        db_client.write_data(data=data)
                        sleep(RATE_LIMIT_REQUEST)
                else:
                    for t in self.tickers:
                        ticker = yf.Ticker(t)
                        history = ticker.history()
                        last_quote = (history.tail(1)['Close'].iloc[0])
                        log.info(last_quote)
            except IndexError as e:
                log.error(e)

            sleep(self.timer)
