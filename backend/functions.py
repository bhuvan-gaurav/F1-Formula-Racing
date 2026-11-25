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
    return response