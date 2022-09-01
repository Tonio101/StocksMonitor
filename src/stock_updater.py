import datetime
import pytz
import holidays
import yfinance as yf

from time import sleep
from threading import Thread
from logger import Logger
log = Logger.getInstance().getLogger()

TIMER_SLEEP_MIN = (5 * 60)
MARKET_CLOSE_SLEEP = (30 * 60)
TIME_ZONE = pytz.timezone('US/Pacific')
US_HOLIDAYS = holidays.US()


class StockStats(Thread):

    def __init__(self, tickers, influxdb_clients=None, timer=TIMER_SLEEP_MIN):
        Thread.__init__(self)
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

    def run(self):
        while True:
            if self.is_market_close():
                sleep(MARKET_CLOSE_SLEEP)
                continue

            try:
                if self.influxdb_clients:
                    # Inject to InfluxDB
                    for name, db_client in self.influxdb_clients.items():
                        ticker = yf.Ticker(name)
                        history = ticker.history()
                        last_quote = (history.tail(1)['Close'].iloc[0])
                        data = ("Price={:0.2f}").format(last_quote)
                        # log.info(data)
                        db_client.write_data(data=data)
                        sleep(2)
                else:
                    for t in self.tickers:
                        ticker = yf.Ticker(t)
                        history = ticker.history()
                        last_quote = (history.tail(1)['Close'].iloc[0])
                        log.info(last_quote)
            except IndexError as e:
                log.error(e)

            sleep(self.timer)
