import re
import requests
from bs4 import BeautifulSoup


def get_matches_urls(team_id):
    page = 1
    urls = set()
    while page:
        url = "http://en.dotabuff.com/esports/teams/" + \
              str(team_id) + \
              "/matches?page=" + \
              str(page)
        source_code = requests.get(url)
        plain_text = source_code.text
        soup = BeautifulSoup(plain_text)
        page_links = soup.find_all(href=re.compile("matches/\d+"))
        for link in page_links:
            href = 'http://en.dotabuff.com' + link.get('href')
            urls.add(href)
            print(href)
        if len(page_links) < 20:
            page = 0
        else:
            page += 1


get_matches_urls('1838315')








