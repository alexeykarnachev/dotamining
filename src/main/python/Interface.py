import datetime
import pickle
from pandas import DataFrame
from DatabaseHandler import DatabaseHandler
from DotaBetsAnalytics import DotaBetsAnalytics
from DotabuffAdapter import DotabuffAdapter
import networkx as nx
import matplotlib.pyplot as plt
from config import *
import scipy as sp
import numpy as np


class Interface:
    """
    This class is high level interface, which combining data obtaining and analytics.
    It is using preset parameters in config.py.
    """

    def __init__(self, con_path):
        self.__db_handler = DatabaseHandler(con_path)

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

    def run_analytics(self):
        if DATES is not None:
            dates = [datetime.datetime.strptime(i, '%Y-%m-%d') for i in DATES]
        else:
            dates = None

        games = GAMES
        min_games = MIN_GAMES

        analytics = DotaBetsAnalytics(self.__db_handler.import_network(dates, games, min_games))

        for i in range(len(TEAMS_AND_OPPONENTS)):
            team = TEAMS_AND_OPPONENTS[i][0]
            opp = TEAMS_AND_OPPONENTS[i][1]
            team_coeff = COEFFS[i][0]
            opp_coeff = COEFFS[i][1]

            team_marginal_winrate = analytics.marginal_winrate(team)
            opp_marginal_winrate = analytics.marginal_winrate(opp)
            team_marginal_ev = analytics.count_ev(team_marginal_winrate, team_coeff)
            opp_marginal_ev = analytics.count_ev(opp_marginal_winrate, opp_coeff)

            team_joint_winrate = analytics.joint_winrate(team, opp)
            opp_joint_winrate = analytics.joint_winrate(opp, team)
            team_joint_ev = analytics.count_ev(team_joint_winrate, team_coeff)
            opp_joint_ev = analytics.count_ev(opp_joint_winrate, opp_coeff)

            team_neighbors_winrate = analytics.joint_neighbors_winrate(team, opp)
            opp_neighbors_winrate = analytics.joint_neighbors_winrate(opp, team)
            team_neighbors_ev = analytics.count_ev(team_neighbors_winrate, team_coeff)
            opp_neighbors_ev = analytics.count_ev(opp_neighbors_winrate, opp_coeff)

            team_name = self.__db_handler.get_team_name(team)
            opp_name = self.__db_handler.get_team_name(opp)

            report = '\nMatch :: {team_name} VS {opp_name}\n' \
                     '-------------------------------------------------------------------------------------------\n' \
                     'Marginal EV   :: {team_name}: {team_marginal_ev:.2f}, {opp_name}: {opp_marginal_ev:.2f}\n' \
                     'Joint EV      :: {team_name}: {team_joint_ev:.2f}, {opp_name}: {opp_joint_ev:.2f}\n' \
                     'Neighbors EV  :: {team_name}: {team_neighbors_ev:.2f}, {opp_name}: {opp_neighbors_ev:.2f}\n' \
                     '-------------------------------------------------------------------------------------------\n'.\
                format(team_name=team_name,
                       opp_name=opp_name,
                       team_marginal_ev=team_marginal_ev,
                       opp_marginal_ev=opp_marginal_ev,
                       team_joint_ev=team_joint_ev,
                       opp_joint_ev=opp_joint_ev,
                       team_neighbors_ev=team_neighbors_ev,
                       opp_neighbors_ev=opp_neighbors_ev)

            print(report)


if __name__ == '__main__':
    I = Interface(CON_PATH)
    I.run_analytics()





