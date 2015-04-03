from sqlalchemy import create_engine, select, join
from sqlalchemy.orm import sessionmaker
from DataModel import *
from DotabuffSpider import DotabuffSpider
from grab.proxylist import ProxyList



class DotabuffAdapter:
    def __init__(self, database_configuration, spider_configuration):
        self.__database_configuration = database_configuration
        self.__spider_configuration = spider_configuration

        engine = create_engine(self.__database_configuration['con_path'])
        session = sessionmaker()
        session.configure(bind=engine)
        Base.metadata.create_all(engine)

        self.__s = session()
        self.__s.autoflush = False

    def __configure_spider(self):
        threads = int(self.__spider_configuration['threads'])
        use_proxy = self.__spider_configuration['use_proxy']
        proxy_file = self.__spider_configuration['proxy_file']
        spider = DotabuffSpider(self.__team_id, self.__ignore_id)

        spider.thread_number = threads

        if use_proxy:
            spider.proxylist = ProxyList(proxy_file, source_type='text_file')
            spider.proxy_auto_change = True
            spider.proxylist_enabled = True

        return spider

    def update_team(self, team_id):
        q = self.__s.query(Match.dotabuff_id).join(Team).filter(Team.dotabuff_id == team_id)
        self.__ignore_id = [i[0] for i in self.__s.execute(q).fetchall()]
        self.__team_id = team_id

        spider = self.__configure_spider()
        spider.run()

        for i in spider.get_results():
            try:
                self.__s.add_all(i)
                self.__s.commit()
            except:
                pass

    def update_opponents(self, team_id):

        q = "SELECT DISTINCT a.dotabuff_id " \
            "FROM team a " \
            "join team b on b.match_id = a.match_id " \
            "where b.dotabuff_id = :team_id " \
            "and a.dotabuff_id != :team_id"

        teams_id = [i[0] for i in self.__s.execute(q, {'team_id': team_id}).fetchall()]
        for i in teams_id:
            self.update_team(i)


