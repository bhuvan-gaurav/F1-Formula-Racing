from fastapi import FastAPI, HTTPException, Header, Body
import functions
from datetime import date
from pydantic import BaseModel,Field

app = FastAPI()
@app.post("/championships", status_code=201)
def add_championship(name:str=Body(), token=Header(None)):
    user = functions.get_current_user(token)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid or expired access token")
    if user.role != "organizer":
        raise HTTPException(status_code=403, detail="Only organizers can create championships")
    return functions.create_championship(organizer_id=user.user_id, name=name)

def get_all_championships():
    session=Session(engine)
    championships=session.query(Championship).all()
    response=[]
    for c in championships:
        response.append({  "id":c.id, "name":c.name,  "organizer_id":c.organizer_id
        })
    session.close()
    return response