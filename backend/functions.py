from sqlalchemy import Integer, String, Boolean, Column, DateTime, create_engine, inspect, ForeignKey
from sqlalchemy.orm import Session, declarative_base
from datetime import datetime,timedelta,timezone
import jwt 
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    name = Column(String)
    email = Column(String, unique=True)
    hashed_password = Column(String)
    role = Column(String)


class Team(Base):
    __tablename__ = "teams"

    id = Column(Integer, primary_key=True)
    name = Column(String)
    country = Column(String)
    manager_id = Column(Integer, ForeignKey("users.id"))
    driver_limit = Column(Integer)


class Driver(Base):
    __tablename__ = "drivers"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True)
    driver_number = Column(Integer)
    team_id = Column(Integer, ForeignKey("teams.id"), nullable=True)
    application_status = Column(String, nullable=True)


class Championship(Base):
    __tablename__ = "championships"

    id = Column(Integer, primary_key=True)
    name = Column(String)
    organizer_id = Column(Integer, ForeignKey("users.id"))


class ChampionshipTeam(Base):
    __tablename__ = "championship_teams"

    id = Column(Integer, primary_key=True)
    championship_id = Column(Integer, ForeignKey("championships.id"))
    team_id = Column(Integer, ForeignKey("teams.id"))


class Race(Base):
    __tablename__ = "races"

    id = Column(Integer, primary_key=True)
    championship_id = Column(Integer, ForeignKey("championships.id"))
    name = Column(String)
    location = Column(String)
    race_date = Column(Date)


class RaceResult(Base):
    __tablename__ = "race_results"

    id = Column(Integer, primary_key=True)
    race_id = Column(Integer, ForeignKey("races.id"))
    driver_id = Column(Integer, ForeignKey("drivers.id"))
    position = Column(Integer)
    points = Column(Integer)
    fastest_lap = Column(String, nullable=True)