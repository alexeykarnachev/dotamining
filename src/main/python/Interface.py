import datetime
import pickle
from pandas import DataFrame
from DatabaseHandler import DatabaseHandler
from DotaBetsAnalytics import DotaBetsAnalytics
from DotabuffAdapter import DotabuffAdapter
import networkx as nx
import matplotlib.pyplot as plt
from config import *


class Interface:
    """
    This class is high level interface, which combining data obtaining and analytics.
    It is using preset parameters in config.py.
    """
    def __init__(self, con_path):
        self.__db_handler = DatabaseHandler(con_path)
        self.__analytics = DotaBetsAnalytics()

    def run_update(self, teams_to_update, threads, use_proxy, proxy_file, update_opponents):
        for team_id in teams_to_update:
            spider_configuration = {'threads': threads,
                                    'use_proxy': use_proxy,
                                    'proxy_file': proxy_file,
                                    'ignore_id': self.__db_handler.get_matches_id(team_id)}
            adapter = DotabuffAdapter(self.__db_handler, spider_configuration)
            adapter.update_team(team_id)
            print('Team Updated :: {}'.format(team_id))
            if update_opponents:
                adapter.update_opponents(team_id)
                print('Team Opponents Updated :: {}'.format(team_id))

    def run_analytics(self, methods):
        for method in methods.keys():
            if method == 'marginal':
                teams_to_analyze = method[method]['teams_to_analyze']
                teams_coeffs = method[method]['teams_coeffs']
                marginal_results = DataFrame(columns=('TeamID', 'TeamName', 'Coeff', 'P', 'Ev', 'Matches', 'LastDate'))
                last_date = methods[method]['last_date']
                last_games = methods[method]['last_games']
                if methods[method]['last_date'] is not None:
                    last_date = datetime.datetime.strptime(methods[method]['last_date'], '%Y-%m-%d')
                if methods[method]['last_games'] is not None:
                    last_games = methods[method]['last_games']
                for i in range(len(teams_to_analyze)):
                    team_id = teams_to_analyze[i]
                    coeff = teams_coeffs[i]
                    name = self.__db_handler.get_team_name(team_id)
                    results = self.__db_handler.get_team_results(team_id, last_date, last_games)
                    matches = len(results)
                    p = self.__analytics.count_p(results)
                    ev = self.__analytics.count_ev(p, coeff)
                    marginal_results.loc[i] = [team_id, name, coeff, p, ev, matches, last_date]
                print(marginal_results)

            if method == 'graph_analysis':
                last_date = methods[method]['last_date']
                last_games = methods[method]['last_games']
                save_graph_path = methods[method]['save_graph_path']
                read_graph_path = methods[method]['read_graph_path']
                graph = self.__db_handler.import_network(last_date, last_games, save_graph_path, read_graph_path)
                self.__analytics.analyze_graph(graph)

if __name__ == '__main__':
    I = Interface(CON_PATH)
    I.run_analytics(GRAPH_ANALYSIS)





