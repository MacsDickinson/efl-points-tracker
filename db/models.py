from sqlalchemy import Column, Integer, String, Date, ForeignKey, UniqueConstraint, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

class League(Base):
    __tablename__ = 'leagues'

    id = Column(Integer, primary_key=True)
    api_id = Column(Integer, unique=True, nullable=False)
    name = Column(String, nullable=False)
    teams = relationship("Team", back_populates="league")
    matches = relationship("Match", back_populates="league")
    standings = relationship("Standings", back_populates="league")

class Team(Base):
    __tablename__ = 'teams'

    id = Column(Integer, primary_key=True)
    api_id = Column(Integer, nullable=False)
    name = Column(String, nullable=False)
    league_id = Column(Integer, ForeignKey('leagues.id'), nullable=False)
    league = relationship("League", back_populates="teams")
    home_matches = relationship("Match", back_populates="home_team", foreign_keys="Match.home_team_id")
    away_matches = relationship("Match", back_populates="away_team", foreign_keys="Match.away_team_id")
    standings = relationship("Standings", back_populates="team")

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
    home_score = Column(Integer, nullable=True)  # Allow null for upcoming matches
    away_score = Column(Integer, nullable=True)  # Allow null for upcoming matches
    status = Column(String, nullable=False)  # FT for finished, NS for not started, etc.

    league = relationship("League", back_populates="matches")
    home_team = relationship("Team", back_populates="home_matches", foreign_keys=[home_team_id])
    away_team = relationship("Team", back_populates="away_matches", foreign_keys=[away_team_id])

    __table_args__ = (
        UniqueConstraint('season', 'league_id', 'home_team_id', 'away_team_id', name='uix_match_teams'),
    )

class Standings(Base):
    __tablename__ = 'standings'

    id = Column(Integer, primary_key=True)
    season = Column(Integer, nullable=False)
    league_id = Column(Integer, ForeignKey('leagues.id'), nullable=False)
    team_id = Column(Integer, ForeignKey('teams.id'), nullable=False)
    position = Column(Integer, nullable=False)
    points = Column(Integer, nullable=False)  # Total points including deductions
    points_deduction = Column(Integer, nullable=False, default=0)  # Store any points deductions
    matches_played = Column(Integer, nullable=False)
    goals_for = Column(Integer, nullable=False)
    goals_against = Column(Integer, nullable=False)
    goal_difference = Column(Integer, nullable=False)
    form = Column(String(5), nullable=True)  # Last 5 matches: W/D/L
    last_updated = Column(DateTime, nullable=False, default=datetime.utcnow)

    league = relationship("League", back_populates="standings")
    team = relationship("Team", back_populates="standings")

    __table_args__ = (
        UniqueConstraint('season', 'league_id', 'team_id', name='uix_standings_team'),
    )