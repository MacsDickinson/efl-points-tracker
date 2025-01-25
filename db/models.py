from sqlalchemy import Column, Integer, String, Date, ForeignKey, UniqueConstraint, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

class League(Base):
    __tablename__ = 'leagues'

    id = Column(Integer, primary_key=True)
    api_id = Column(Integer, unique=True, nullable=False)
    name = Column(String, nullable=False)
    teams = relationship("Team", back_populates="league")
    matches = relationship("Match", back_populates="league")

class Team(Base):
    __tablename__ = 'teams'

    id = Column(Integer, primary_key=True)
    api_id = Column(Integer, nullable=False)  # Removed unique constraint
    name = Column(String, nullable=False)
    league_id = Column(Integer, ForeignKey('leagues.id'), nullable=False)
    league = relationship("League", back_populates="teams")
    home_matches = relationship("Match", back_populates="home_team", foreign_keys="Match.home_team_id")
    away_matches = relationship("Match", back_populates="away_team", foreign_keys="Match.away_team_id")

    __table_args__ = (
        UniqueConstraint('api_id', 'league_id', name='uix_team_api_league'),
    )

class Match(Base):
    __tablename__ = 'matches'

    id = Column(Integer, primary_key=True)
    api_id = Column(Integer, unique=True, nullable=False)
    date = Column(Date, nullable=False)
    season = Column(Integer, nullable=False)
    league_id = Column(Integer, ForeignKey('leagues.id'), nullable=False)
    home_team_id = Column(Integer, ForeignKey('teams.id'), nullable=False)
    away_team_id = Column(Integer, ForeignKey('teams.id'), nullable=False)
    home_score = Column(Integer)
    away_score = Column(Integer)
    status = Column(String, nullable=False)  # FT for finished, NS for not started, etc.

    league = relationship("League", back_populates="matches")
    home_team = relationship("Team", back_populates="home_matches", foreign_keys=[home_team_id])
    away_team = relationship("Team", back_populates="away_matches", foreign_keys=[away_team_id])

    __table_args__ = (
        UniqueConstraint('season', 'league_id', 'home_team_id', 'away_team_id'),
    )