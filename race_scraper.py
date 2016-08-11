from splinter import Browser
from redis import StrictRedis
import time
import datetime

redis = StrictRedis()
redis.flushdb()


class RaceScraper(object):

    def __init__(self, base_url=None):
        self.browser = Browser(driver_name='phantomjs')
        self.base_url = base_url

        self.redis = StrictRedis()

    def add_to_redis(self, race):
        if race['name'] not in self.redis.smembers('races'):
            self.redis.sadd('races', race)


def get_race_data(name, date, location, source_url, website=None, distance=None, race_type=None, unmapped=None):

    race_data = {
        'name': name,
        'date': parse_date(date),
        'distance': distance,
        'location': location,
        'sourceUrl': source_url,
        'race_website': website,
        'race_type': race_type,
        'unmapped': unmapped,
        'timestamp': time.time()
    }

    return race_data


def parse_date(x):
    d = None

    try:
        d = datetime.datetime.strptime(x, "%m/%d/%Y")
    except ValueError:
        pass
    try:
        d = datetime.datetime.strptime(x, "%m-%d-%Y")
    except ValueError:
        pass
    try:
        d = datetime.datetime.strptime(x, "%b %d, %Y")
    except ValueError:
        pass
    try:
        d = datetime.datetime.strptime(x, "%B %d, %Y")
    except ValueError:
        pass
    try:
        d = datetime.datetime.strptime(x, "%d %b %Y")
    except ValueError:
        pass
    try:
        d = datetime.datetime.strptime(x, "%Y/%m/%d")
    except ValueError:
        pass
    try:
        d = datetime.datetime.strptime(x, "%m%d%Y")
    except ValueError:
        pass
    try:
        d = datetime.datetime.strptime(x, "%Y%m%d")
    except ValueError:
        pass

    return d.strftime("%m/%d/%Y")


