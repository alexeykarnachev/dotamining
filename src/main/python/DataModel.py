from sqlalchemy import Column, DateTime, String, Integer, ForeignKey, func, Date, Boolean
from sqlalchemy.orm import relationship, backref
from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base()
"""
This set of classes is database objects representation in python objects.
"""


class Match(Base):
    """
    Match object.
    """
    # Tablename.
    __tablename__ = 'match'
    # Match id in database.
    id = Column(Integer, primary_key=True)
    # Match dotabuff id.
    dotabuff_id = Column(Integer, unique=True)
    # Match insert time in base.
    insert_time = Column(DateTime, default=func.now())
    # Duration of the match (seconds).
    duration = Column(Integer)
    # Date of the match.
    date = Column(DateTime)
    # Dotabuff id of the league (only pro-matches, else none).
    league_dotabuff_id = Column(Integer)
    # Dotabuff name of the league (only pro-matches, else none).
    league_dotabuff_name = Column(String)
    # Dotabuff name of the game mode.
    mode_dotabuff_name = Column(String)
    # Dotabuff name of the game region.
    region_dotabuff_name = Column(String)
    # Dotabuff name of the game skill (only public-matches, else none).
    skill_dotabuff_name = Column(String)
    # Dotabuff lobby name (only public-matches, else none).
    lobby_dotabuff_name = Column(String)


class Team(Base):
    """
    Team object.
    """
    # Tablename.
    __tablename__ = 'team'
    # Team id in database.
    id = Column(Integer, primary_key=True)
    # Team dotabuff name.
    dotabuff_name = Column(String)
    # Team dotabuff id.
    dotabuff_id = Column(Integer)
    # Team fraction (Radiant or Dire).
    fraction = Column(String)
    # Team match result (0 - Loose, 1 - Win)
    win = Column(Boolean)
    # Match id in database, ForeignKey.
    match_id = Column(Integer, ForeignKey('match.id'))

    # Match relationship.
    match = relationship(Match)


class Player(Base):
    """
    Player object.
    """
    # Tablename.
    __tablename__ = 'player'
    # Player id in database.
    id = Column(Integer, primary_key=True)
    # Team id in database, ForeignKey.
    team_id = Column(Integer, ForeignKey('team.id'))
    # Player dotabuff name.
    dotabuff_name = Column(String)
    # Player dotabuff id.
    dotabuff_id = Column(Integer)
    # Player's hero dotabuff name.
    hero_dotabuff_name = Column(String)
    # If player leaved the match (0 - Did not leave, 1 - Leave).
    abandoned = Column(Boolean)
    # Final player level on the end of match.
    level = Column(Integer)
    # Final player kills on the end of match.
    k = Column(Integer)
    # Final player deaths on the end of match.
    d = Column(Integer)
    # Final player assists on the end of match.
    a = Column(Integer)
    # Final player gold on the end of match.
    gold = Column(Integer)
    # Final player last hits on the end of match.
    lh = Column(Integer)
    # Final player denies on the end of match.
    dn = Column(Integer)
    # Average player experiences points per minute.
    xpm = Column(Integer)
    # Average player gold per minute.
    gpm = Column(Integer)
    # Overall player hero damage per minute.
    hd = Column(Integer)
    # Overall player hero heall per minute.
    hh = Column(Integer)
    # Overall player tower damage per minute.
    td = Column(Integer)

    # Team relationship.
    team = relationship(Team)


class Item(Base):
    """
    Item object.
    """
    # Tablename.
    __tablename__ = 'item'
    # Item id in database.
    id = Column(Integer, primary_key=True)
    # Player id in database, ForeignKey.
    player_id = Column(Integer, ForeignKey('player.id'))
    # Item dotabuff name.
    dotabuff_name = Column(String)

    # Player relationship.
    player = relationship(Player)
