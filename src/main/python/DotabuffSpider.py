import re
import datetime
from grab import Grab
from grab.spider import Spider, Task
from bs4 import BeautifulSoup as bs
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from DataModel import *


class DotabuffSpider(Spider):

    def __init__(self, team_id, ignore_id):
        super().__init__()
        self.__team_id = team_id
        self.__ignore_id = ignore_id

    def __parse_match_grab(self, match_grab):
        def __parse_duration(str):
            split = str.split(':')
            if len(split) == 3:
                return int(split[0]) * 60 * 60 + int(split[1]) * 60 + int(split[2])
            elif len(split) == 2:
                return int(split[0]) * 60 + int(split[1])

        def __parse_k_as_thousands(str):
            if re.match('.+k', str):
                digits = float(re.sub('k', '', str)) * 1000
            else:
                digits = float(str)
            return int(digits)

        sibling_text = lambda x: x.next_sibling.text if x is not None else None

        match = Match()
        teams = []
        players = []
        items = []

        soup = bs(match_grab.doc.body)
        match.dotabuff_id = int(
            re.findall('\d+', soup.find('div', attrs={'class': 'content-header-title'}).text)[0])
        match.date = datetime.datetime.strptime(soup.find('time')['datetime'][0:19], '%Y-%m-%dT%H:%M:%S')
        match.duration = __parse_duration(sibling_text(soup.find('dt', text='Duration')))
        match.skill_dotabuff_name = sibling_text(soup.find('dt', text='Skill Bracket'))
        match.lobby_dotabuff_name = sibling_text(soup.find('dt', text='Lobby Type'))
        match.mode_dotabuff_name = sibling_text(soup.find('dt', text='Game Mode'))
        match.region_dotabuff_name = sibling_text(soup.find('dt', text='Region'))
        match.league_dotabuff_name = sibling_text(soup.find('dt', text='League'))
        if match.league_dotabuff_name:
            match.league_dotabuff_id = int(re.findall('\d+', soup.find('dt', text='League').
                                                             next_sibling.find('a')['href'])[0])

        if 'Radiant' in soup.find('div', text=re.compile('Radiant|Dire Victory')).text:
            result = 'radiant'
        else:
            result = 'dire'

        for team_class in ['radiant', 'dire']:
            team = Team(match=match, fraction=team_class)
            if result == team_class:
                team.win = 1
            else:
                team.win = 0
            section = soup.find('section', {'class': team_class})
            try:
                header = section.find('header', {'style': 'vertical-align: middle'}).find_all('a')[1]
                team.dotabuff_id = int(re.findall('\d+', header['href'])[0])
                team.dotabuff_name = header.text
            except:
                pass
            teams.append(team)

            table = section.find('tbody')
            for row in table.childGenerator():
                player = Player(team=team)
                player.hero_dotabuff_name = re.findall(re.compile('heroes/(.+)'), row.find('a')['href'])[0]
                try:
                    player_ahref = row.find_all('a', {'href': re.compile('players/(.+)')})[1]
                    player.dotabuff_name = player_ahref.find('img')['alt']
                    player.dotabuff_id = int(re.findall('\d+', player_ahref['href'])[0])
                except:
                    pass

                columns = row.find_all('td')

                try:
                    abandoned = columns[1].find('div', {'class': 'subtext abandoned'}).text
                    if abandoned == 'Abandoned':
                        player.abandoned = 1
                except:
                    player.abandoned = 0

                player.level = int(columns[3].text)
                player.k = __parse_k_as_thousands(columns[4].text)
                player.d = __parse_k_as_thousands(columns[5].text)
                player.a = __parse_k_as_thousands(columns[6].text)
                player.gold = __parse_k_as_thousands(columns[7].text)
                player.lh = __parse_k_as_thousands(columns[8].text)
                player.dn = __parse_k_as_thousands(columns[9].text)
                player.xpm = __parse_k_as_thousands(columns[10].text)
                player.gpm = __parse_k_as_thousands(columns[11].text)
                player.hd = __parse_k_as_thousands(columns[12].text)
                player.hh = __parse_k_as_thousands(columns[13].text)
                player.td = __parse_k_as_thousands(columns[14].text)

                items_a = columns[15].find_all('a')
                for item_i in range(len(items_a)):
                    item = Item(player=player)
                    item.dotabuff_name = re.findall(re.compile('items/(.+)'), items_a[item_i]['href'])[0]
                    items.append(item)
                players.append(player)

        return [match] + items + players + teams

    def __get_team_pagination_links(self, team_matches_grab):
        soup = bs(team_matches_grab.doc.body)
        team_id = int(re.findall('\d+', soup.find('h1').find('a')['href'])[0])
        pagination = soup.find('nav', attrs={'class': 'pagination'})
        if pagination:
            number = int(re.findall(re.compile('.+page=(\d+)'), str(pagination.find('span', {'class': 'last'})))[0])
        else:
            number = 1

        pages = ['http://www.dotabuff.com/esports/teams/{id}/matches?page={p}'.format(id=team_id, p=p)
                 for p in range(1, number + 1)]
        return pages

    def __get_valid_matches_from_pagination_grab(self, pagination_grab, ignore_id):
        soup = bs(pagination_grab.doc.body)
        rows = soup.find('tbody').find_all('tr', class_=lambda x: x != 'inactive')
        links = []
        for row in rows:
            str_match_id = row.find('a')['href']
            match_id = int(re.findall('\d+', str_match_id)[0])
            if match_id not in ignore_id:
                links.append('http://www.dotabuff.com' + str_match_id)

        return links

    def prepare(self):
        self.initial_urls = ['http://www.dotabuff.com/esports/teams/{id}/matches'.format(id=self.__team_id)]
        self.__results = []

    def task_initial(self, grab, task):
        try:
            pagination_links = self.__get_team_pagination_links(grab)
        except:
            pagination_links = []

        for pagination_link in pagination_links:
            yield Task('pagination_link', url=pagination_link)

    def task_pagination_link(self, grab, task):
        try:
            matches_links = self.__get_valid_matches_from_pagination_grab(grab, self.__ignore_id)
        except:
            matches_links = []

        for match_link in matches_links:
            yield Task('match_link', url=match_link)

    def task_match_link(self, grab, task):
        try:
            match = self.__parse_match_grab(grab)
            self.__results += [match]
        except:
            pass

    def get_results(self):
        return self.__results