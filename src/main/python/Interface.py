import datetime
from pandas import DataFrame
from DatabaseHandler import DatabaseHandler
from DotaBetsAnalytics import DotaBetsAnalytics
from DotabuffAdapter import DotabuffAdapter
from DotabuffSpider import DotabuffSpider
from config import *


class Interface:
    def __init__(self):
        self.__db_handler = DatabaseHandler(CON_PATH)
        self.__analytics = DotaBetsAnalytics()

    def run_update(self):
        for team_id in TEAMS_TO_UPDATE:
            spider_configuration = {'threads': THREADS,
                                    'use_proxy': USE_PROXY,
                                    'proxy_file': PROXY_FILE,
                                    'ignore_id': self.__db_handler.get_matches_id(team_id)}
            adapter = DotabuffAdapter(self.__db_handler, spider_configuration)
            adapter.update_team(team_id)
            print('Team Updated :: {}'.format(team_id))
            if UPDATE_OPPONENTS:
                adapter.update_opponents(team_id)
                print('Team Opponents Updated :: {}'.format(team_id))

    def run_analytics(self):
        for method in METHODS.keys():

            if method == 'marginal':
                marginal_results = DataFrame(columns=('TeamID', 'TeamName', 'Coeff', 'P', 'Ev', 'Matches', 'LastDate'))
                last_date = METHODS[method]['last_date']
                last_games = METHODS[method]['last_games']
                if METHODS[method]['last_date'] is not None:
                    last_date = datetime.datetime.strptime(METHODS[method]['last_date'], '%Y-%m-%d')
                if METHODS[method]['last_games'] is not None:
                    last_games = METHODS[method]['last_games']
                for i in range(len(TEAMS_TO_ANALYZE)):
                    team_id = TEAMS_TO_ANALYZE[i]
                    coeff = TEAMS_COEFFS[i]
                    name = self.__db_handler.get_team_name(team_id)
                    results = self.__db_handler.get_team_results(team_id, last_date, last_games)
                    matches = len(results)
                    p = self.__analytics.count_marginal_p(results)
                    ev = self.__analytics.count_ev(p, coeff)
                    marginal_results.loc[i] = [team_id, name, coeff, p, ev, matches, last_date]
                print(marginal_results)



