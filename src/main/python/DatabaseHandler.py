from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from DataModel import *


class DatabaseHandler:
    def __init__(self, database_configuration):
        self.__database_configuration = database_configuration

        engine = create_engine(self.__database_configuration['con_path'])
        session = sessionmaker()
        session.configure(bind=engine)
        Base.metadata.create_all(engine)

        self.__s = session()
        self.__s.autoflush = False

    def get_match_by_id(self, match_id):
        self.__s.rollback()
        q = self.__s.query(Match).filter(Match.dotabuff_id == match_id)

        return self.__s.execute(q).fetchall()[0]

    def get_matches_id_by_team_id(self, team_id):
        q = self.__s.query(Match.dotabuff_id).join(Team).filter(Team.dotabuff_id == team_id)

        return [i[0] for i in self.__s.execute(q).fetchall()]

    def get_opponents_id(self, team_id):
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

    def commit_spider_results(self, spider_results):
        self.__s.rollback()
        for i in spider_results:
            try:
                self.__s.add_all(i)
                self.__s.commit()
            except:
                pass

        if len(spider_results):
            for i in spider_results[0]:
                if type(i) is Team:
                    team_id = i.dotabuff_id
                    print('{} matches parsed :: Team {}'.format(len(spider_results), team_id))
                    break

