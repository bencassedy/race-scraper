__author__ = 'bencassedy'

from race_scraper import RaceScraper, get_race_data
from datetime import datetime
from multiprocessing import Pool
import time
from selenium.common.exceptions import WebDriverException
from redis import StrictRedis
import json


BASE_URL = 'http://www.racingcolorado.com/index.php?page=calendars&event_type=running'

scraper = RaceScraper(base_url=BASE_URL)

scraper.browser.visit(scraper.base_url)

next_button = scraper.browser.select("no_per_page", "10000")  # show all results

today = datetime.today()
today = today.strftime("%m/%d/%Y")

race_list = []
redis = StrictRedis()
redis.flushdb()


def get_race_colorado_races():
    race_rows = scraper.browser.find_by_xpath('//form[@name="del"]/following-sibling::tr')
    for r in race_rows:
        race_date = r.find_by_xpath('./td[2]').text.encode('ascii')
        race_link = r.find_by_xpath('./a[contains(text(), "details")]')
        race_name = r.find_by_xpath('./td[4]').encode('ascii')
        race_link = race_link['href']
        race_location = r.find_by_xpath('./td[5]').text.encode('ascii')
        race_type = r.find_by_xpath('./td[3]').text.encode('ascii')

        redis.rpush('racing_colo_queue', get_race_data(
            name=race_name,
            date=race_date,
            location=race_location,
            source_url=BASE_URL,
            website=race_link,
            race_type=race_type
        ))


def update_races(race_datum):
    s = RaceScraper()
    # race_datum = None
    # print race_datum
    # while redis.llen('run_usa_queue') > 0:
    try:
        # race_datum = redis.blpop('run_usa_queue')[1]
        race_datum = race_datum.replace(" u'", " '")
        race_datum = race_datum.replace(" \'", " \"")
        race_datum = race_datum.replace("\',", "\",")
        race_datum = race_datum.replace("{\'", "{\"")
        race_datum = race_datum.replace("\'}", "\"}")
        race_datum = race_datum.replace("\':", "\":")
        race_datum = race_datum.replace(' None,', ' \"None\",')
        race_datum = json.loads(race_datum)
        s.browser.visit(race_datum['race_website'])
        race_datum['race_website'] = s.browser.url
        redis.rpush('races', race_datum)
        s.browser.quit()
    except WebDriverException:  # if it doesn't grab the url, just pass along what we have
        redis.rpush('races', race_datum)


start_crawl = time.time()
crawl_pool = Pool(len(page_range))
crawl_pool.map(paginate_results, page_range)
crawl_pool.close()
crawl_pool.join()
end_crawl = time.time()
crawl_time = end_crawl - start_crawl
print "crawl took: " + str(crawl_time)

start_scrape = time.time()
scrape_pool = Pool(20)  # took 350 seconds with 20 procs
scrape_pool.map(update_races, redis.lrange('run_usa_queue', 0, -1))
scrape_pool.close()
scrape_pool.join()
end_scrape = time.time()
scrape_time = end_scrape - start_scrape
print "scrape took: " + str(scrape_time)


# start_single_scrape = time.time()
# races = [update_races(race) for race in redis.lrange('run_usa_queue', 0, -1)]
# print races
# end_single_scrape = time.time()
# single_scrape_time = end_single_scrape - start_single_scrape
# print "single_scrape took: " + str(single_scrape_time)