import yfinance as yf

from time import sleep
from threading import Thread
from logger import Logger
log = Logger.getInstance().getLogger()

TIMER_SLEEP_MIN = (5 * 60)


class StockStats(Thread):

    def __init__(self, tickers, influxdb_clients=None, timer=TIMER_SLEEP_MIN):
        Thread.__init__(self)
        self.tickers = tickers
        self.influxdb_clients = influxdb_clients
        self.timer = timer

    def run(self):
        while True:
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
