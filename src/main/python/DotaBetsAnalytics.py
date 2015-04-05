import configparser
from DatabaseHandler import DatabaseHandler


class DotaBetsAnalytics:
    def __init__(self, database_configuration, analytics_configuration):
        self.__db_handler = DatabaseHandler(database_configuration)
        self.__team_1_id = int(analytics_configuration['team_1_id'])
        self.__team_2_id = int(analytics_configuration['team_2_id'])
        self.__team_1_coeff = float(analytics_configuration['team_1_coeff'])
        self.__team_2_coeff = float(analytics_configuration['team_2_coeff'])

    def count_marginal_ev(self):
        team_1_results = self.__db_handler.get_team_results(self.__team_1_id)
        team_2_results = self.__db_handler.get_team_results(self.__team_2_id)

        team_1_winrate = sum(team_1_results)/len(team_1_results)
        team_2_winrate = sum(team_2_results)/len(team_2_results)

        team_1_ev = 1 + (team_1_winrate * (self.__team_1_coeff - 1) - (1 - team_1_winrate) * 1)
        team_2_ev = 1 + (team_2_winrate * (self.__team_2_coeff - 1) - (1 - team_2_winrate) * 1)

        return team_1_ev, team_2_ev, len(team_1_results), len(team_2_results)