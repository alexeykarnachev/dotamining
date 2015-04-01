from sqlalchemy import Column, DateTime, String, Integer, ForeignKey, func, Date, Boolean
from sqlalchemy.orm import relationship, backref
from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base()
 
 
class Match(Base):
    __tablename__ = 'match'
    id = Column(Integer, primary_key=True)
    dotabuff_id = Column(Integer, unique=True)
    insert_time = Column(DateTime, default=func.now())
    duration = Column(Integer)
    date = Column(DateTime)
    league_dotabuff_id = Column(Integer)
    league_dotabuff_name = Column(String)
    mode_dotabuff_name = Column(String)
    region_dotabuff_name = Column(String)
    skill_dotabuff_name = Column(String)
    lobby_dotabuff_name = Column(String)


class Team(Base):
    __tablename__ = 'team'
    id = Column(Integer, primary_key=True)
    dotabuff_name = Column(String)
    dotabuff_id = Column(Integer)
    fraction = Column(String)
    win = Column(Boolean)
    match_id = Column(Integer, ForeignKey('match.id'))

    match = relationship(Match)


class Player(Base):
    __tablename__ = 'player'
    id = Column(Integer, primary_key=True)
    team_id = Column(Integer, ForeignKey('team.id'))
    dotabuff_name = Column(String)
    dotabuff_id = Column(Integer)
    hero_dotabuff_name = Column(String)
    abandoned = Column(Boolean)
    level = Column(Integer)
    k = Column(Integer)
    d = Column(Integer)
    a = Column(Integer)
    gold = Column(Integer)
    lh = Column(Integer)
    dn = Column(Integer)
    xpm = Column(Integer)
    gpm = Column(Integer)
    hd = Column(Integer)
    hh = Column(Integer)
    td = Column(Integer)

    team = relationship(Team)


class Item(Base):
    __tablename__ = 'item'
    id = Column(Integer, primary_key=True)
    player_id = Column(Integer, ForeignKey('player.id'))
    dotabuff_name = Column(String)

    player = relationship(Player)



#
# m = Match(league_dotabuff_id=1, dotabuff_id=1000)
# t_1 = Team(dotabuff_name="Team_1", dotabuff_id=1, fraction='radiant', match=m)
# t_2 = Team(dotabuff_name="Team_2", dotabuff_id=2, fraction='dire', match=m)
# p_1 = Player(dotabuff_name='Player_1', dotabuff_id=100, hero_dotabuff_name='hero_1', team=t_1)
# p_2 = Player(dotabuff_name='Player_2', dotabuff_id=200, hero_dotabuff_name='hero_2', team=t_2)
# s = session()
# s.add_all([m,t_1,t_2,p_1,p_2])
# s.commit()