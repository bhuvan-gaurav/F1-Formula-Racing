from sqlalchemy import Integer, String, Boolean, Column, DateTime, create_engine, inspect, ForeignKey
from sqlalchemy.orm import Session, declarative_base
from sqlalchemy import Column, Integer, String, Date, ForeignKey
from datetime import datetime,timedelta,timezone,date
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
    session.close()
    access_token=create_token(username=username,token_type="access")
    refresh_token=create_token(username=username,token_type="refresh")
    return {"access_token":access_token,"refresh_token":refresh_token,"user_id":user.user_id}
    
    
def create_token(username,token_type):
    time=ACCESS_TOKEN_EXPIRE_MINUTES
    if token_type == "refresh":
        time=REFRESH_TOKEN_EXPIRY
    payload = {
        "username": username,
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
        return payload["username"]
    return False

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

def get_current_user(token):
    username = verify_token(token, "access")
    if not username:
        return False
    session = Session(engine)
    user = session.query(User).filter_by(user_name=username).first()
    session.close()
    return user

def reg_driver(user_id,name,country,date_of_birth,experience_years):
    session=Session(engine)
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