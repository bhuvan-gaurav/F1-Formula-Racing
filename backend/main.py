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

@app.get("/teams/{team_id}")
def team_details(team_id:int):
    result = functions.get_team_details(team_id)
    if not result:
        raise HTTPException(status_code=404, detail="Team not found")
    return result

@app.post("/races", status_code=201)
def add_race(championship_id:int=Body(), name:str=Body(), location:str=Body(), race_date:date=Body(), token=Header(None)):
    user = functions.get_current_user(token)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid or expired access token")
    if user.role != "organizer":
        raise HTTPException(status_code=403, detail="Only organizers can schedule races")
    return functions.schedule_race(championship_id=championship_id, name=name, location=location, race_date=race_date)

@app.get("/championships/{championship_id}/races")
def list_races(championship_id:int):
    result = functions.get_races(championship_id)
    if result is False:
        raise HTTPException(status_code=404, detail="Championship not found")
    return result

@app.post("/results", status_code=201)
def add_results(race_id:int=Body(), results:list=Body(), token=Header(None)):
    user = functions.get_current_user(token)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid or expired access token")
    if user.role != "organizer":
        raise HTTPException(status_code=403, detail="Only organizers can submit results")
    return functions.submit_results(race_id=race_id, results=results)