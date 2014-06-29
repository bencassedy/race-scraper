from splinter import Browser

BASE_URL = 'http://www.trailrunnermag.com/index.php/races/race-calendar?city=&state=CO&country=&name=&startdate=&enddate=&view=list'
            
class RaceScraper(Browser):
def get_races(races):
    if races:
        for bat in races:
            print bat.find_by_xpath('.//b').text
    else:
        print "there aren't any races"

browser = Browser('phantomjs')
browser.visit('http://casker.com/races.html')
races = browser.find_by_xpath("//td[@class='hmmain']/table")
get_races(races)

while True:
    try:
        browser.find_by_xpath('//a[contains(text(), "Next")]').click()
        get_races(browser.find_by_xpath("//td[@class='hmmain']/table"))
    except:
        print "No more races"
        break

