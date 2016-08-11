__author__ = 'bencassedy'

from race_scraper import RaceScraper, get_race_data
from celery import group
from celery_app import celery
from datetime import datetime
from multiprocessing import Pool
import time
from redis import StrictRedis

BASE_URL = 'http://www.trailrunnermag.com/index.php/races/race-calendar#'

redis = StrictRedis()
redis.flushdb()
scraper = RaceScraper(base_url=BASE_URL)

# fill out the search form
scraper.browser.visit(scraper.base_url)
scraper.browser.find_by_xpath('//select[@name="state"]//option[@value="CO"]').click()
today = datetime.today()
today = today.strftime("%m/%d/%Y")
scraper.browser.find_by_xpath('//input[@id="startdate"]').fill(today)
scraper.browser.find_by_xpath('//input[@id="find-races"]').click()

time.sleep(2)

races = scraper.browser.find_by_xpath('//div[@id="race-calendar"]//tr')
races.pop(0)


# get the races
def get_trailrunner_races():
    race_list = []
    for r in races:
        race_name_data = r.find_by_xpath('.//td[2]')
        race_link = r.find_by_xpath('.//td[2]/a')['href']
        race_name = race_name_data.text
        race_date = r.find_by_xpath('.//td[1]').text
        race_length = r.find_by_xpath('.//td[3]').text
        race_length.replace('\x1d', ',')
        race_location = r.find_by_xpath('.//td[4]').text

        race_list.append(get_race_data(
            name=race_name,
            date=race_date,
            location=race_location,
            source_url=BASE_URL,
            website=race_link,
            distance=race_length,
            race_type='trail'
        ))
    return race_list


# get the rest of the race data and send it to redis
def update_race(race_datum):
    s = RaceScraper()
    s.browser.visit(race_datum['race_website'])
    try:
        race_datum['race_website'] = s.browser.find_by_xpath(
            '//span[contains(text(), "WEBSITE:")]/following-sibling::a').text
        redis.sadd('tr_races', race_datum)
    except AttributeError:
        print 'unable to scrape {}'.format(race_datum['name'])


# enable multiple procs to scrape race links
def run():
    race_list = get_trailrunner_races()
    pool = Pool(16)
    pool.map(update_race, race_list)
    pool.close()
    pool.join()

