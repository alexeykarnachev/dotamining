import pickle
import pandas as pd
from sqlalchemy import create_engine, desc
from sqlalchemy.orm import sessionmaker
from DataModel import *
import networkx as nx
import numpy as np


class DatabaseHandler:
    """
    This class is a handler for dotabuff base. Using for fetching query results and commit spider results.
    """

    def __init__(self, con_path):
        """
        Constructor for DatabaseHandler.
        :param con_path: Connection string for engine initializing and session creation.
        :return:
        """

        # Initialize engine and create session.
        engine = create_engine(con_path)
        session = sessionmaker()
        session.configure(bind=engine)
        Base.metadata.create_all(engine)

        # Session autoflush off. See 'sqlalchemy autoflush'.
        self.__s = session()
        self.__s.autoflush = False

    def get_match(self, match_id):
        """
        Method for getting match instance from match id.
        :param match_id: Str. or int. Match dotabuff id.
        :return: Match object tuple.
        """
        # Rollback session.
        self.__s.rollback()

        # Creating query for match fetching.
        q = self.__s.query(Match).filter(Match.dotabuff_id == match_id)

        return self.__s.execute(q).fetchall()[0]

    def get_teams_id(self):
        """
        Method for getting all teams id in data base.
        :return: Match object tuple.
        """
        # Rollback session.
        self.__s.rollback()

        # Creating query for match fetching.
        q = self.__s.query(Team.dotabuff_id).distinct()

        return [i[0] for i in self.__s.execute(q).fetchall()]

    def get_team_name(self, team_id):
        """
        Method for getting team name from team id.
        :param team_id: Str. or int. Team dotabuff id.
        :return: Team name as string.
        """
        # Rollback session.
        self.__s.rollback()

        # Creating query for team name fetching.
        q = self.__s.query(Team.dotabuff_name).filter(Team.dotabuff_id == team_id)

        return self.__s.execute(q).fetchall()[0][0]

    def get_matches_id(self, team_id):
        """
        Method for getting team name from team id.
        :param team_id: Str. or int. Team dotabuff id.
        :return: List of matches id.
        """
        # Rollback session.
        self.__s.rollback()

        # Creating query for matches id fetching.
        q = self.__s.query(Match.dotabuff_id).join(Team).filter(Team.dotabuff_id == team_id)

        return [i[0] for i in self.__s.execute(q).fetchall()]

    def get_opponents_id(self, team_id):
        """
        Method for getting all opponents teams id for chosen team.
        :param team_id: Str. or int. Team dotabuff id.
        :return: List of opponents dotabuff id.
        """
        # Rollback session.
        self.__s.rollback()

        # Creating query for opponents id fetching.
        q = "SELECT DISTINCT a.dotabuff_id " \
            "FROM team a " \
            "join team b on b.match_id = a.match_id " \
            "where b.dotabuff_id = :team_id " \
            "and a.dotabuff_id != :team_id"

        return [i[0] for i in self.__s.execute(q, {'team_id': team_id}).fetchall()]

    def get_join_matches_id(self, team_1_id, team_2_id):
        """
        Method for getting all join matches id for two teams.
        :param team_1_id: Str. or int. Team dotabuff id.
        :param team_2_id: Str. or int. Team dotabuff id.
        :return: List of join matches id.
        """
        # Rollback session.
        self.__s.rollback()

        # Creating query for matches id (database id) fetching.
        q = "SELECT DISTINCT a.match_id " \
            "FROM team a " \
            "join team b on b.match_id = a.match_id " \
            "where b.dotabuff_id = :team_1_id " \
            "and a.dotabuff_id = :team_2_id"

        # Fetch all join matches id (database id).
        matches_id = [i[0] for i in self.__s.execute(q, {'team_1_id': team_1_id, 'team_2_id': team_2_id}).fetchall()]
        join_matches_id = []

        # Get all join matches dotabuff id due to database id.
        for match_id in matches_id:
            # Creating query for fetching match dotabuff id due to its database id.
            q = self.__s.query(Match.dotabuff_id).filter(Match.id == match_id)

            # Execute query and fetch match dotabuff id.
            join_matches_id.append(self.__s.execute(q).fetchall()[0][0])

        return join_matches_id

    def get_team_results(self, team_id, last_date=None, last_games=None, opponent=None):
        """
        Method for getting team results vector within specific parameters.
        :param team_id: Str. or int. Team dotabuff id.
        :param last_date: Datetime object.
        :param last_games: Amount of last matches as integer.
        :param opponent: Opponent dotabuff id as integer (get team result vector relative to opponent id).
        :return: Binary result list.
        """
        # Rollback session.
        self.__s.rollback()

        # If opponent is none, fetch team matches results ignoring opponents.
        if opponent is None:
            # Creating query for fetching match results ignoring opponents.
            q = self.__s.query(Team.win).filter(Team.dotabuff_id == team_id).join(Match).order_by(desc(Match.date))

            # Filter query within last_date parameter, if it is not none.
            if last_date is not None:
                q = q.filter(Match.date >= last_date)

            # Filter query within last_games parameter, if it is not none.
            if last_games is not None:
                q = q.limit(last_games)

            # Fetch the results.
            results = [i[0] for i in self.__s.execute(q).fetchall()]

        # If opponent is not none, fetch team matches results within the opponent.
        else:
            # Get join matches id.
            matches_id = self.get_join_matches_id(team_id, opponent)
            results = []

            # Go through all join matches...
            for match_id in matches_id:
                # And create query for fetching this match result.
                q = self.__s.query(Team.win).filter(Team.dotabuff_id == team_id).join(Match).filter(
                    Match.dotabuff_id == match_id).order_by(desc(Match.date))

                # Filter query within last_date parameter, if it is not none.
                if last_date is not None:
                    q = q.filter(Match.date >= last_date)

                # Filter query within last_games parameter, if it is not none.
                if last_games is not None:
                    q = q.limit(last_games)

                # Fetch the results.
                results.append([i for i in self.__s.execute(q).fetchall()][0][0])

        return results

    def commit_spider_results(self, spider_results):
        """
        Procedure for committing spider results into database.
        :param spider_results: Spider results list (see DotabuffSpider).
        :return:
        """
        # Rollback session.
        self.__s.rollback()

        # Go through all spider results.
        for i in spider_results:
            # Try to:
            try:
                # Add result and commit.
                self.__s.add_all(i)
                self.__s.commit()
            except:
                pass

    def import_network(self, dates=None, games=None, min_games=None):
        graph = nx.DiGraph()

        q = 'SELECT a.dotabuff_id, b.dotabuff_id, a.win, a.match_id ' \
            'FROM team a ' \
            'join team b on b.match_id = a.match_id ' \
            'join match m on m.id = a.match_id ' \
            'where a.dotabuff_name != b.dotabuff_name ' \

        if dates is not None:
            q += 'and m.date >= :from_date ' \
                 'and m.date <= :to_date '\
                 'order by m.date desc'
            df = pd.DataFrame(self.__s.execute(q, {'from_date': dates[0], 'to_date': dates[1]}).fetchall(),
                              columns=('TeamID', 'OpponentID', 'Result', 'Matches'))
        else:
            q += 'order by m.date desc'
            df = pd.DataFrame(self.__s.execute(q).fetchall(),
                              columns=('TeamID', 'OpponentID', 'Result', 'Matches'))

        if games is None:
            from_game = 0
            to_game = None
        else:
            from_game = games[0]
            to_game = games[1]

        df = df.groupby(['TeamID', 'OpponentID'], squeeze=True).agg({'Result': lambda x: np.sum(x[from_game: to_game]),
                                                                     'Matches': lambda x: len(x[from_game: to_game])})
        if min_games is None:
            min_games = 0

        def __add_edge(x):
            if x['Matches'] >= min_games:
                graph.add_weighted_edges_from([x.name + (x['Result']/x['Matches'],)], matches=x['Matches'])

        df.apply(__add_edge, 1)

        return graph

    def __save_object(self, obj, filename):
        with open(filename, 'wb') as output:
            pickle.dump(obj, output, pickle.HIGHEST_PROTOCOL)

    def __load_object(self, filename):
        with open(filename, "rb") as input_file:
            return pickle.load(input_file)
