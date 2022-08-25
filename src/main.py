import argparse
import json
import os
import sys

from stock_updater import StockStats
from influxdb_client import InfluxDbClient

from logger import Logger
log = Logger.getInstance().getLogger()


def parse_config_file(fname: str) -> dict:
    """

    Args:
        fname (str): _description_

    Returns:
        dict: _description_
    """
    with open(os.path.abspath(fname), 'r') as fp:
        data = json.load(fp)
        return data


def configure_influxdb_stock_tickers(config):
    """

    Args:
        config (_type_): _description_

    Returns:
        _type_: _description_
    """
    influx_db_clients = dict()

    influxdb_info = config['influxdb']
    url = influxdb_info['url']
    username = influxdb_info['auth']['user']
    passwd = influxdb_info['auth']['pasw']
    dbName = influxdb_info['dbName']

    for ticker in influxdb_info['stocks_tickers']:
        ticker_name = ticker['name']
        measurement = ticker['measurement']
        tag_set = (ticker['tagSet']).format(
            ticker_name
        )
        field_set = ticker['fieldSet']

        influx_db_clients[ticker_name] = \
            InfluxDbClient(url=url,
                           auth=(username, passwd),
                           db_name=dbName,
                           measurement=measurement,
                           tag_set=tag_set,
                           field_set=field_set)

    return influx_db_clients


def main(argv):
    usage = ("{FILE} --config <config_file> --debug").format(FILE=__file__)
    description = 'Stock Statistics'
    parser = argparse.ArgumentParser(usage=usage, description=description)
    parser.add_argument("-c", "--config", help="Configuration file",
                        required=True)
    parser.add_argument("--debug", help="Enable verbose logging",
                        action='store_true', required=False)
    parser.set_defaults(debug=False)

    args = parser.parse_args()
    config = parse_config_file(args.config)
    influxDbEnabled = config['features']['enableInfluxDb']
    influxdb_clients = None

    if influxDbEnabled:
        influxdb_clients = configure_influxdb_stock_tickers(config)

    stocks = \
        StockStats(tickers=config['tickers'],
                   influxdb_clients=influxdb_clients)
    stocks.start()
    stocks.join()


if __name__ == '__main__':
    main(sys.argv)
