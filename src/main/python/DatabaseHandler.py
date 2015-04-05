from datetime import datetime
from sqlalchemy import create_engine, desc
from sqlalchemy.orm import sessionmaker, Query
from DataModel import *


class DatabaseHandler:
    def __init__(self, con_path):
        engine = create_engine(con_path)
        session = sessionmaker()
        session.configure(bind=engine)
        Base.metadata.create_all(engine)

        self.__s = session()
        self.__s.autoflush = False

    def get_match(self, match_id):
        self.__s.rollback()
        q = self.__s.query(Match).filter(Match.dotabuff_id == match_id)

        return self.__s.execute(q).fetchall()[0]

    def get_team_name(self, team_id):
        self.__s.rollback()
        q = self.__s.query(Team.dotabuff_name).filter(Team.dotabuff_id == team_id)

        return self.__s.execute(q).fetchall()[0][0]

    def get_matches_id(self, team_id):
        self.__s.rollback()
        q = self.__s.query(Match.dotabuff_id).join(Team).filter(Team.dotabuff_id == team_id)

        return [i[0] for i in self.__s.execute(q).fetchall()]

    def get_opponents_id(self, team_id):
        self.__s.rollback()
        q = "SELECT DISTINCT a.dotabuff_id " \
            "FROM team a " \
            "join team b on b.match_id = a.match_id " \
            "where b.dotabuff_id = :team_id " \
            "and a.dotabuff_id != :team_id"

        return [i[0] for i in self.__s.execute(q, {'team_id': team_id}).fetchall()]

    def get_join_matches_id(self, team_1_id, team_2_id):
        self.__s.rollback()
        q = "SELECT DISTINCT a.match_id " \
            "FROM team a " \
            "join team b on b.match_id = a.match_id " \
            "where b.dotabuff_id = :team_1_id " \
            "and a.dotabuff_id = :team_2_id"
        matches_id = [i[0] for i in self.__s.execute(q, {'team_1_id': team_1_id, 'team_2_id': team_2_id}).fetchall()]
        join_matches_id = []
        for match_id in matches_id:
            q = self.__s.query(Match.dotabuff_id).filter(Match.id == match_id)
            join_matches_id.append(self.__s.execute(q).fetchall()[0][0])

        return join_matches_id

    def get_team_results(self, team_id, last_date=None, last_games=None, opponent=None):
        self.__s.rollback()
        if opponent is None:
            q = self.__s.query(Team.win).filter(Team.dotabuff_id == team_id).join(Match).order_by(desc(Match.date))
            if last_date is not None:
                q = q.filter(Match.date >= last_date)
            if last_games is not None:
                q = q.limit(last_games)
            results = [i[0] for i in self.__s.execute(q).fetchall()]
        else:
            matches_id = self.get_join_matches_id(team_id, opponent)
            results = []
            for match_id in matches_id:
                q = self.__s.query(Team.win).filter(Team.dotabuff_id == team_id).join(Match).filter(
                    Match.dotabuff_id == match_id).order_by(desc(Match.date))
                if last_date is not None:
                    q = q.filter(Match.date >= last_date)
                if last_games is not None:
                    q = q.limit(last_games)
                results.append([i for i in self.__s.execute(q).fetchall()][0][0])
        return results

    def commit_spider_results(self, spider_results):
        self.__s.rollback()
        for i in spider_results:
            try:
                self.__s.add_all(i)
                self.__s.commit()
            except:
                pass


