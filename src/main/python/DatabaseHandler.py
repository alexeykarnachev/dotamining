import pickle
from sqlalchemy import create_engine, desc
from sqlalchemy.orm import sessionmaker
from DataModel import *
import networkx as nx


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

    def get_team_id(self):
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

    def import_network(self, last_date=None, last_games=None, save_graph_path=None, read_graph_path=None):
        graph = nx.DiGraph()
        teams_id = self.get_team_id()

        if read_graph_path is not None:
            graph = self.__load_object(read_graph_path)
        else:
            i = 0
            for team_id in teams_id[0:-1]:
                for opponent_id in teams_id[teams_id.index(team_id) + 1:]:
                    try:
                        results = self.get_team_results(team_id, last_date, last_games, opponent_id)
                    except:
                        break
                    if len(results) == 0:
                        break
                    else:
                        team_weight = 1 - sum(results)/len(results)
                        opp_weight = 1 - team_weight
                        edge_from_team = (team_id, opponent_id, team_weight)
                        edge_from_opp = (opponent_id, team_id, opp_weight)
                        graph.add_weighted_edges_from([edge_from_team, edge_from_opp], matches=len(results))
                print(i)
                i += 1

            if save_graph_path is not None:
                self.__save_object(graph, save_graph_path)

        return graph

    def __save_object(self, obj, filename):
        with open(filename, 'wb') as output:
            pickle.dump(obj, output, pickle.HIGHEST_PROTOCOL)

    def __load_object(self, filename):
        with open(filename, "rb") as input_file:
            return pickle.load(input_file)

