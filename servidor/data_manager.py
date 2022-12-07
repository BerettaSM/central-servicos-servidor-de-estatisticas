import datetime as dt
import logging

import requests

from .utils import get_jwt

logging.basicConfig(level=logging.DEBUG, format=' %(asctime)s - %(levelname)s - %(message)s')

FETCH_INTERVAL = 60  # seconds


def has_interval_elapsed_since_datetime(datetime: dt.datetime, interval_in_seconds: int):
    if datetime is None:
        return False
    now: dt.datetime = dt.datetime.now()
    elapsed: dt.timedelta = now - datetime
    return elapsed.total_seconds() >= interval_in_seconds


class DataManager:

    def __init__(self):
        self.request_headers = None
        self.ticket_data = None
        self.last_fetched = None

    def _fetch(self):
        if not self.ticket_data or has_interval_elapsed_since_datetime(self.last_fetched, FETCH_INTERVAL):
            logging.info('DataManager - Fetching fresh data from database.')
            res = requests.get(f'http://localhost:8080/api/ticket/unpaginated', headers=self.request_headers)
            self.ticket_data = res.text
            self.last_fetched = dt.datetime.now()
        else:
            logging.info(f'DataManager - {FETCH_INTERVAL} seconds have not yet passed. Sending cached data.')

    def get_data(self):
        if self.request_headers is None:
            self._get_headers()
        self._fetch()
        return self.ticket_data

    def _get_headers(self):
        self.request_headers = {
            'Authorization': f'Bearer {get_jwt()}'
        }
