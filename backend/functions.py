from sqlalchemy import Integer, String, Boolean, Column, DateTime, create_engine, inspect, ForeignKey
from sqlalchemy.orm import Session, declarative_base
from datetime import datetime,timedelta,timezone
import jwt 
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError

ph=PasswordHasher()
DB_PATH = "FormulaRacing.db"
engine = create_engine(f"sqlite:///{DB_PATH}")
Base = declarative_base()
ACCESS_TOKEN_EXPIRE_MINUTES = 15
REFRESH_TOKEN_EXPIRY=7*24*60
SECRET_KEY ="SECRET067"
ALGORITHM = "HS256"


def create_championship(organizer_id,name):
    session=Session(engine)
    new_championship=Championship(name=name,organizer_id=organizer_id)
    session.add(new_championship)
    session.commit()
    response={ "id":new_championship.id, "name":new_championship.name,"organizer_id":new_championship.organizer_id
    }
    session.close()
    return response


def get_all_championships():
    session=Session(engine)
    championships=session.query(Championship).all()
    response=[]
    for c in championships:
        response.append({
            "id":c.id,
            "name":c.name,
            "organizer_id":c.organizer_id
        })
    session.close()
    return 

def get_team_details(team_id):
    session=Session(engine)
    team=session.query(Team).filter_by(id=team_id).first()
    if team is None:
        session.close()
        return False
    response={"id":team.id,"name":team.name,"country":team.country,"manager_id":team.manager_id,"driver_limit":team.driver_limit}
    session.close()
    return response

def schedule_race(championship_id,name,location,race_date):
    session=Session(engine)
    championship=session.query(Championship).filter_by(id=championship_id).first()
    if championship is None:
        session.close()
        return False
    new_race=Race(championship_id=championship_id,name=name,location=location,race_date=race_date)
    session.add(new_race)
    session.commit()
    response={"id":new_race.id,"championship_id":new_race.championship_id,"name":new_race.name,"location":new_race.location,"race_date":new_race.race_date}
    session.close()
    return response


def get_races(championship_id):
    session=Session(engine)
    championship=session.query(Championship).filter_by(id=championship_id).first()
    if championship is None:
        session.close()
        return False
    response=[]
    for r in session.query(Race).filter_by(championship_id=championship_id).all():
        response.append({"id":r.id,"name":r.name,"location":r.location,"race_date":r.race_date})
    session.close()
    return response


POINTS={1:25,2:18,3:15,4:12,5:10,6:8,7:6,8:4,9:2,10:1}

def submit_results(race_id,results): 
    session=Session(engine)
    race=session.query(Race).filter_by(id=race_id).first()
    if race is None:
        session.close()
        return False
    saved=[]
    for r in results:
        points=POINTS.get(r["position"],0)
        session.add(RaceResult(race_id=race_id,driver_id=r["driver_id"],position=r["position"],points=points,fastest_lap=r.get("fastest_lap")))
        saved.append({"driver_id":r["driver_id"],"position":r["position"],"points":points})
    session.commit()
    session.close()
    return {"race_id":race_id,"results":saved}