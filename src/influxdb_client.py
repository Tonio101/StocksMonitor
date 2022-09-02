import requests

from enum import Enum
from logger import Logger
log = Logger.getInstance().getLogger()


class TickerType(Enum):
    UNKNOWN = 0
    STOCKS = 1
    CRYPTO = 2


class InfluxDbClient(object):

    def __init__(self, url, auth, db_name, measurement, tag_set, field_set):
        """_summary_
        Influx db interface client.

        Args:
            url (string): Influx DB URL
            auth (string): Auth tuple (username, password)
            db_name (string): Influx Database Name
            measurement (string): Measurement
            tag_set (string): Measurement tag set
            field_set (string): Measurement field set
        """
        self.url = url
        self.auth = auth
        self.db = db_name
        self.params = (
            ('db', db_name),
        )
        self.headers = {'Content-Type': 'application/json'}
        self.measurement = measurement
        self.tag_set = tag_set
        self.field_set = field_set

    def set_url(self, url):
        self.url = url

    def set_auth(self, auth):
        self.auth = auth

    def set_db(self, db_name):
        self.db = db_name
        self.params = (
            ('db', db_name),
        )

    def get_type(self) -> TickerType:
        if "stock_stats" in self.measurement:
            return TickerType.STOCKS
        elif "crypto_stats" in self.measurement:
            return TickerType.CRYPTO
        return TickerType.UNKNOWN

    def write_data(self, data):
        """
        Send data to Influx DB via POST request.

        Args:
            data (string): "field_set=<val>"

        Returns:
            int: 0 if successful, else error
        """
        data = ("{0},{1} {2}").format(
            self.measurement,
            self.tag_set,
            data
        )
        log.debug(data)
        response = requests.post(url=self.url,
                                 params=self.params,
                                 data=data,
                                 auth=self.auth,
                                 headers=self.headers)
        log.debug(response)

        if response.status_code == 204:
            log.debug(("Successfully sent data [{0}] to influx db "
                       "Elapsed time {1}").format(
                        data,
                        response.elapsed
                      ))
            return 0

        log.error("Error to send data [{0}] to influx db {1}".format(
            data,
            response.status_code
        ))

        return response.status_code
