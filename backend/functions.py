from sqlalchemy import Integer, String, Column, Date, create_engine, ForeignKey
from sqlalchemy.orm import Session, declarative_base
from datetime import datetime, timedelta, timezone
import jwt
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError

ph = PasswordHasher()
DB_PATH = "data/f1.db"
engine = create_engine(f"sqlite:///{DB_PATH}")
Base = declarative_base()
ACCESS_TOKEN_EXPIRE_MINUTES = 15
REFRESH_TOKEN_EXPIRY = 7 * 24 * 60
SECRET_KEY = "SECRET067"
ALGORITHM = "HS256"


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

def create_organizer(user_name, password):
    session = Session(engine)
    user_exists = session.query(User).filter_by(email=user_name).first()
    if user_exists is not None:
        session.close()
        return False
    new_user = User(name=user_name, email=user_name, hashed_password=ph.hash(password), role="organizer")
    session.add(new_user)
    session.commit()
    result = {"id": new_user.id, "name": new_user.name, "role": new_user.role}
    session.close()
    return result


def create_team(name, country, manager_id, driver_limit):
    session = Session(engine)

    manager = session.query(User).filter_by(id=manager_id).first()
    if manager is None:
        session.close()
        return False

    team_exists = session.query(Team).filter_by(name=name).first()
    if team_exists is not None:
        session.close()
        return False

    new_team = Team(name=name, country=country, manager_id=manager_id, driver_limit=driver_limit)
    session.add(new_team)
    session.commit()
    result = {
        "id": new_team.id,
        "name": new_team.name,
        "country": new_team.country,
        "manager_id": new_team.manager_id,
        "driver_limit": new_team.driver_limit
    }
    session.close()
    return result

def get_teams():
    session = Session(engine)
    result = []
    for team in session.query(Team).all():
        count = session.query(Driver).filter_by(team_id=team.id).count()
        result.append({"id": team.id, "name": team.name, "country": team.country,
                       "manager_id": team.manager_id, "driver_limit": team.driver_limit,
                       "driver_count": count})
    session.close()
    return result

def get_standings(championship_id):
    session = Session(engine)
    championship = session.query(Championship).filter_by(id=championship_id).first()
    if championship is None:
        session.close()
        return False

    points = {}
    races = session.query(Race).filter_by(championship_id=championship_id).all()
    for race in races:
        results = session.query(RaceResult).filter_by(race_id=race.id).all()
        for result in results:
            if result.driver_id not in points:
                points[result.driver_id] = 0
            points[result.driver_id] += result.points

    standings = []
    for driver_id in points:
        standings.append({"driver_id": driver_id, "points": points[driver_id]})
    standings.sort(key=get_points, reverse=True)

    session.close()
    return standings

def get_driver_history(driver_id):
    session = Session(engine)
    driver = session.query(Driver).filter_by(id=driver_id).first()
    if driver is None:
        session.close()
        return False

    history = []
    total_points = 0
    results = session.query(RaceResult).filter_by(driver_id=driver_id).all()
    for result in results:
        total_points += result.points
        history.append({"race_id": result.race_id, "position": result.position, "points": result.points})

    session.close()
    return {"driver_id": driver_id, "total_points": total_points, "history": history}
