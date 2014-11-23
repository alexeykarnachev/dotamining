from grab import Grab, GrabError
import re
from game import *
from urllib.parse import quote

'''
Functions for parse dotabuff, eGamingBets and find free proxies
'''
# ==================================================================
# Proxy Finder:
# ==================================================================

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


# =================================================================
# Valid matches urls finder:
#================================================================

def get_valid_matches_urls_from_matches_page_grab(grab):
    #============================================================
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


    #============================================================
    # Parse matches section:

    # Go through all valid rows and find:

    # matches ids:
    matches_urls_valid = [grab.make_url_absolute(tr[x].select('td[1]/a').
                                                 attr_list('href').pop())
                          for x in good_matches_indices]

    return matches_urls_valid


#================================================================
# Matches pages finder
#================================================================

def get_matches_pages_urls_from_matches_page_grab(grab):
    #============================================================
    # Find number of pages:

    last_page_elem = \
        grab.doc.select("//*[@id='page-content']/section/"
                        "article/nav/span[@class='last']/a")
    if last_page_elem.exists():
        number_of_pages = int(re.findall(
            '\d+$', last_page_elem.attr('href')).pop())
    else:
        number_of_pages = 1

    #============================================================
    # Generate pages urls:

    matches_pages_urls = [grab.make_url_absolute(str('./matches?page={p}').
                                                 format(p=i + 1))
                          for i in range(number_of_pages)]

    return (matches_pages_urls)


#================================================================
# Initial teams matches pages finder:
#================================================================

def get_teams_matches_pages_urls_from_teams_page_grab(grab):
    teams_matches_pages_urls = \
        [grab.make_url_absolute(x) + "/matches" for x in
         grab.doc.select("//*[@id='teams-all']/table/tbody"
                         "/tr/td[2]/a").attr_list('href')]
    return teams_matches_pages_urls


#================================================================
# Single match parser:
#================================================================

def parse_game_object_from_match_page_grab(grab):
    #============================================================
    # Parse match section:

    # Get match id
    match_id = int(re.findall('\d+',
                              grab.doc.select('//*[@id="content-header-primary"]'
                                              '/div/h1').text()).pop())

    # Get match result
    match_result_str = grab.doc.select('//*[@id="page-content"]'
                                       '/div[3]/div[1]').text()
    if match_result_str == 'Radiant Victory':
        match_result = 0
    if match_result_str == 'Dire Victory':
        match_result = 1

    # Get match date
    match_date = grab.doc.select('//*[@id="content-header-'
                                 'secondary"]/dl[5]/dd').text()

    # Get match region
    match_region = grab.doc.select('//*[@id="content-header-'
                                   'secondary"]/dl[3]/dd').text()

    # Get match league
    match_league = grab.doc.select('//*[@id="content-header-'
                                   'secondary"]/dl[1]/dd/a').text()

    # Get radiant team name
    radiant_name = grab.doc.select('//*[@id="page-content"]/div[3]/'
                                   'div[2]/section[1]/header/a[2]').text()

    # Get dire team name
    dire_name = grab.doc.select('//*[@id="page-content"]/div[3]/'
                                'div[2]/section[2]/header/a[2]').text()

    # Get radiant team id
    radiant_id = int(re.findall('\d+$', grab.doc.select(
        '//*[@id="page-content"]/div[3]/div[2]/section[1]'
        '/header/a[2]').attr('href')).pop())

    # Get dire team id
    dire_id = int(re.findall('\d+$', grab.doc.select(
        '//*[@id="page-content"]/div[3]/div[2]/section[2]'
        '/header/a[2]').attr('href')).pop())

    # Get radiant players names
    radiant_players_names = grab.doc.select(
        '//*[@id="page-content"]/div[3]/div[2]/section[1]'
        '/article/table/tbody/tr/td[2]/a').text_list()

    # Get dire players names
    dire_players_names = grab.doc.select(
        '//*[@id="page-content"]/div[3]/div[2]/section[2]'
        '/article/table/tbody/tr/td[2]/a').text_list()

    # Get radiant players ids
    radiant_players_ids = [int(re.findall('\d+$', x).pop())
                           for x in grab.doc.select(
            '//*[@id="page-content"]/div[3]/div[2]/section[1]'
            '/article/table/tbody/tr/td[2]/a').attr_list('href')]

    # Get dire players ids
    dire_players_ids = [int(re.findall('\d+$', x).pop())
                        for x in grab.doc.select(
            '//*[@id="page-content"]/div[3]/div[2]/section[2]'
            '/article/table/tbody/tr/td[2]/a').attr_list('href')]

    #============================================================
    # Create db object - gp:
    gp = GamePast({'match_id': match_id,
                   'date': match_date,
                   'league': match_league,
                   'region': match_region,
                   'result': match_result,
                   'prediction': -1,
                   'team_radiant': {
                       'id': [radiant_id],
                       'name': [radiant_name]
                   },
                   'team_dire': {
                       'id': [radiant_id, dire_id],
                       'name': [radiant_name, dire_name]
                   },
                   'players_radiant': {
                       'id': radiant_players_ids,
                       'name': radiant_players_names
                   },
                   'players_dire': {
                       'id': dire_players_ids,
                       'name': dire_players_names
                   }}
    )

    return gp


if __name__ == '__main__':
    g = Grab()
    g.go('http://en.dotabuff.com/matches/1042720490')
    foo = parse_game_object_from_match_page_grab(g)
    print(foo.as_str())
