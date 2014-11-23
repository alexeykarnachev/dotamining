from grab import Grab
import re
from urllib.parse import quote
'''
Functions for parse dotabuff, eGamingBets and find free proxies
'''
# ===========================================================
# Proxy Finder:


def proxy_finder(txt_path):

    g = Grab()
    g.go('http://www.google.ru/search?num=100&q=' +
         quote('free proxy +":8080"'))
    rex = re.compile(r'(?:(?:[-a-z0-9]+\.)+)[a-z0-9]+:\d{2,4}')
    f = open(txt_path, 'w')
    proxies = rex.findall(g.doc.select('//body').text().replace(" ", ""))
    print(len(proxies))
    for proxy in proxies:
        g.setup(proxy=proxy, proxy_type='http', connect_timeout=5,
                timeout=5)
        try:
            g.go('http://google.com')
        except GrabError:
            print(proxy, 'FAIL')
        else:
            print(proxy, 'OK')
            f.write(proxy + '\n')
    f.close()


def get_valid_matches_urls_from_matches_page(team_id, page_number):

    # ===========================================================
    # Grab section:

    grab = Grab()
    url = ('http://en.dotabuff.com/esports/teams/{i}/'
           'matches?page={p}').format(i=team_id, p=page)
    grab.go(url)


    # ===========================================================
    # Filter matches section:

    # Select all rows in table:
    tr = grab.doc.select('//*[@id="page-content"]/section/'
                         'article/table/tbody/tr')
    # Find opponents' links in table:
    opponent_links = [x.select('td[2]/a').attr_list('href')
                      for x in tr]
    # Find heroes in table:
    team_heroes = [x.select('td[4]/div/a').attr_list('href')
                   for x in tr]
    opponent_heroes = [x.select('td[5]/div/a').attr_list('href')
                       for x in tr]
    # Find inactive games in table:
    inactive_games = [x.attr('class', default='active')
                      for x in tr]

    # Find bad matches(indices starts from 0):
    unknown_indices = [i for i, x in enumerate(opponent_links)
                       if len(x) == 0]
    bad_team_heroes_indices = [i for i, x in enumerate(team_heroes)
                               if len(x) < 5]
    bad_opponent_heroes_indices = [i for i, x in enumerate(opponent_heroes)
                                   if len(x) < 5]
    inactive_games_indices = [i for i, x in enumerate(inactive_games)
                              if x != 'active']

    bad_matches_indices = set(unknown_indices +
                              bad_team_heroes_indices +
                              bad_opponent_heroes_indices +
                              inactive_games_indices)
    # Find good matches(indices starts from 0):
    good_matches_indices = {i for i in range(len(tr))} \
        .difference(bad_matches_indices)


    # ===========================================================
    # Parse matches section:

    # Go through all valid rows and find:

    # matches ids:
    matches_ids_valid = [grab.make_url_absolute(tr[x].select('td[1]/a').
                         attr_list('href').pop())
                         for x in good_matches_indices]

    return matches_ids_valid