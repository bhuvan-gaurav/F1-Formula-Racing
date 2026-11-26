from sqlalchemy import Integer, String, Column,create_engine,ForeignKey
from sqlalchemy.orm import Session, declarative_base
from sqlalchemy import Column, Integer, String, Date, ForeignKey
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
POINTS={1:25,2:18,3:15,4:12,5:10,6:8,7:6,8:4,9:2,10:1}



class User(Base):
    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True)    
    user_name = Column(String, unique=True)
    password = Column(String)
    role = Column(String, default="driver")


class Team(Base):
    __tablename__ = "teams"

    id = Column(Integer, primary_key=True)
    name = Column(String)
    country = Column(String)
    manager_id = Column(Integer, ForeignKey("users.user_id"))    
    driver_limit = Column(Integer)

class Driver(Base):
    __tablename__ = "drivers"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.user_id"), unique=True)    
    name = Column(String)
    country = Column(String)
    date_of_birth = Column(Date)    
    experience_years = Column(Integer)
    team_id = Column(Integer, ForeignKey("teams.id"), nullable=True)
    application_status = Column(String, nullable=True)

class Championship(Base):
    __tablename__ = "championships"

    id = Column(Integer, primary_key=True)
    name = Column(String)
    organizer_id = Column(Integer, ForeignKey("users.user_id"))    

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

Base.metadata.create_all(engine)


def register_user(user_name:str,password:str,role:str="driver"):
    session = Session(engine)
    user_exists=session.query(User).filter_by(user_name=user_name).first()
    if user_exists is not None:
        session.close()
        return False
    session.add(User(user_name=user_name,password=ph.hash(password),role=role))
    session.commit()
    session.close()
    return True


def verify_login(username, password):
    session=Session(engine)
    user=session.query(User).filter_by(user_name=username).first()
    if user is None:
        session.close()
        return False
    try:
        ph.verify(user.password,password)
    except VerifyMismatchError:
        session.close()
        return False
    role = user.role
    user_id = user.user_id
    session.close()
    access_token=create_token(username=username,token_type="access",role=role)
    refresh_token=create_token(username=username,token_type="refresh",role=role)
    return {"access_token":access_token,"refresh_token":refresh_token,"user_id":user_id,"role":role}
    
    
def create_token(username,token_type,role):
    time=ACCESS_TOKEN_EXPIRE_MINUTES
    if token_type == "refresh":
        time=REFRESH_TOKEN_EXPIRY
    payload = {
        "username": username,
        "role": role,
        "token_type": token_type,
        "exp": datetime.now(timezone.utc) + timedelta(minutes=time)

    }
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    return token


def verify_token( token, token_type):
    try:
        payload = jwt.decode(jwt=token, key=SECRET_KEY, algorithms=[ALGORITHM])
    except:
        return False   
    if payload["token_type"] == token_type:
        return payload
    return False

def get_current_user(token):
    payload = verify_token(token, "access")
    if not payload:
        return False
    session = Session(engine)
    user = session.query(User).filter_by(user_name=payload["username"]).first()
    session.close()
    return user


def create_organizer(user_name, password):
    session = Session(engine)
    user_exists = session.query(User).filter_by(user_name=user_name).first()
    if user_exists is not None:
        session.close()
        return False
    new_user = User(user_name=user_name, password=ph.hash(password), role="organizer")
    session.add(new_user)
    session.commit()
    result = {"id": new_user.user_id, "user_name": new_user.user_name, "role": new_user.role}
    session.close()
    return result


def create_team(name, country, manager_id, driver_limit):
    session = Session(engine)

    manager = session.query(User).filter_by(user_id=manager_id).first()
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
        count = session.query(Driver).filter_by(team_id=team.id, application_status="accepted").count()
        result.append({"id": team.id, "name": team.name, "country": team.country,
                       "manager_id": team.manager_id, "driver_limit": team.driver_limit,
                       "driver_count": count})
    session.close()
    return result

def get_team_details(team_id):
    session=Session(engine)
    team=session.query(Team).filter_by(id=team_id).first()
    if team is None:
        session.close()
        return False
    response={"id":team.id,"name":team.name,"country":team.country,"manager_id":team.manager_id,"driver_limit":team.driver_limit}
    session.close()
    return response


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
    return response


def reg_driver(user_id,name,country,date_of_birth,experience_years):
    session=Session(engine)
    exists=session.query(Driver).filter_by(user_id=user_id).first()
    if exists is not None:
        session.close()
        return False
    new_driver=Driver(user_id=user_id,name=name,country=country,date_of_birth=date_of_birth,experience_years=experience_years)
    session.add(new_driver)
    session.commit()
    response={
        "id":new_driver.id,
        "user_id":new_driver.user_id,
        "name":new_driver.name,
        "country":new_driver.country,
        "date_of_birth":new_driver.date_of_birth,
        "experience_years":new_driver.experience_years
    }
    session.close()
    return response

def apply_to_team(user_id,team_id):
    session=Session(engine)
    driver=session.query(Driver).filter_by(user_id=user_id).first()
    if driver is None:
        session.close()
        return False
    team=session.query(Team).filter_by(id=team_id).first()
    if team is None:
        session.close()
        return False
    if driver.application_status in ("pending","accepted"):
        session.close()
        return False
    driver.team_id=team_id
    driver.application_status="pending"
    session.commit()
    response={"driver_id":driver.id,"team_id":driver.team_id,"application_status":driver.application_status}
    session.close()
    return response

def decide_application(user_id,driver_id,decision):
    session=Session(engine)
    driver=session.query(Driver).filter_by(id=driver_id).first()
    if driver is None or driver.application_status != "pending":
        session.close()
        return False
    team=session.query(Team).filter_by(id=driver.team_id).first()
    if team.manager_id != user_id:
        session.close()
        return False
    if decision == "accepted":
        count=session.query(Driver).filter_by(team_id=team.id,application_status="accepted").count()
        if count >= team.driver_limit:
            session.close()
            return False
        driver.application_status="accepted"
    elif decision == "rejected":
        driver.application_status="rejected"
        driver.team_id=None
    else:
        session.close()
        return False
    session.commit()
    response={"driver_id":driver.id,"team_id":driver.team_id,"application_status":driver.application_status}
    session.close()
    return response

def register_team_for_championship(user_id,championship_id):
    session=Session(engine)
    team=session.query(Team).filter_by(manager_id=user_id).first()
    if team is None:
        session.close()
        return False
    championship=session.query(Championship).filter_by(id=championship_id).first()
    if championship is None:
        session.close()
        return False
    already=session.query(ChampionshipTeam).filter_by(championship_id=championship_id,team_id=team.id).first()
    if already is not None:
        session.close()
        return False
    entry=ChampionshipTeam(championship_id=championship_id,team_id=team.id)
    session.add(entry)
    session.commit()
    response={"id":entry.id,"championship_id":entry.championship_id,"team_id":entry.team_id}
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


def submit_results(race_id,results): 
    session=Session(engine)
    race=session.query(Race).filter_by(id=race_id).first()
    if race is None:
        session.close()
        return False
    for r in results:
        driver=session.query(Driver).filter_by(id=r["driver_id"]).first()
        if driver is None or driver.application_status != "accepted":
            session.close()
            return False
        registered=session.query(ChampionshipTeam).filter_by(championship_id=race.championship_id,team_id=driver.team_id).first()
        if registered is None:
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
    standings.sort(key=lambda s: s["points"], reverse=True)

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

