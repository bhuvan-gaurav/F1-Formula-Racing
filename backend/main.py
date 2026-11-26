from fastapi import FastAPI, HTTPException, Header, Body
import functions
from datetime import date
from pydantic import BaseModel,Field

app = FastAPI()

ROLES = ["admin", "driver"]

def authorize(token, allowed_roles):
    payload = functions.verify_token(token=token, token_type="access")
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid or Expired token")
    if payload["role"] not in allowed_roles:
        raise HTTPException(status_code=403, detail="You do not have permission to do this")
    return payload

@app.post("/register")
def register_user(user_name=Body(), password=Body(), role:str=Body("driver")):
    if role not in ROLES:
        raise HTTPException(status_code=400, detail="Role must be admin or driver")
    if functions.register_user(user_name=user_name, password=password, role=role):
        return {"message": "User registered successfully"}
    raise HTTPException(status_code=409, detail="User already exists")

@app.post("/login")
def login(username=Body(), password=Body()):
    token = functions.verify_login(username=username, password=password)
    if not token:
        raise HTTPException(status_code=401, detail="Invalid username or password")
    return token

@app.post("/refresh")
def refresh_token(refresh_token=Header(None)):
    payload = functions.verify_token(token=refresh_token, token_type="refresh")
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid or expired refresh token")
    access_token = functions.create_token(username=payload["username"], token_type="access", role=payload["role"])
    return {"access_token": access_token}



@app.post("/organizers", status_code=201)
def creating_organizer(user_name=Body(), password=Body(), token=Header(None)):
    authorize(token, ["admin"])
    result = functions.create_organizer(user_name, password)
    if not result:
        raise HTTPException(status_code=409, detail="User already exists")
    return result


@app.post("/teams", status_code=201)
def creating_team(name: str, country: str, manager_id: int, driver_limit: int, token=Header(None)):
    authorize(token, ["admin"]) # changed: replaced manual token & role check with authorize
    result = functions.create_team(name, country, manager_id, driver_limit)
    if not result:
        raise HTTPException(status_code=400, detail="Manager not found or team already exists")
    return result


@app.get("/teams")
def get_teams():
    return functions.get_teams()

@app.get("/championships")
def list_championships():
    return functions.get_all_championships()

@app.get("/teams/{team_id}")
def team_details(team_id:int):
    result = functions.get_team_details(team_id)
    if not result:
        raise HTTPException(status_code=404, detail="Team not found")
    return result


@app.post("/championships", status_code=201)
def add_championship(name:str=Body(), token=Header(None)):
    authorize(token, ["organizer"]) # changed: replaced manual token & role check with authorize
    user = functions.get_current_user(token)
    return functions.create_championship(organizer_id=user.user_id, name=name)


@app.post("/Drivers🏎️", status_code=201)
def register_driver(name:str=Body(), country:str=Body(), date_of_birth:date=Body(), experience_years:int=Body(), token=Header(None)):
    authorize(token, ["driver"]) # changed: replaced manual token & role check with authorize
    user = functions.get_current_user(token)
    results=functions.reg_driver(user_id=user.user_id,name=name,country=country,date_of_birth=date_of_birth,experience_years=experience_years)
    if not results:
        raise HTTPException(status_code=400, detail="Driver profile already exists")
    return results


@app.post("/drivers/apply")
def apply_team(team_id:int=Body(), token=Header(None)):
    authorize(token, ["driver"]) # changed: replaced manual token & role check with authorize
    user = functions.get_current_user(token=token)
    result = functions.apply_to_team(user_id=user.user_id, team_id=team_id)
    if not result:
        raise HTTPException(status_code=400, detail="No driver profile, team not found, or already applied")
    return result

@app.patch("/applications")
def decide(driver_id:int=Body(), decision:str=Body(), token=Header(None)):
    authorize(token, ["admin", "organizer", "driver"]) # changed: replaced manual token check with authorize
    user = functions.get_current_user(token=token)
    result = functions.decide_application(user_id=user.user_id, driver_id=driver_id, decision=decision)
    if not result:
        raise HTTPException(status_code=400, detail="Not your team, no pending application, wrong decision, or team is full")
    return result

@app.post("/championships/register", status_code=201)
def register_team(championship_id:int=Body(), token=Header(None)):
    authorize(token, ["admin", "organizer", "driver"]) # changed: replaced manual token check with authorize
    user = functions.get_current_user(token)
    result = functions.register_team_for_championship(user_id=user.user_id, championship_id=championship_id)
    if not result:
        raise HTTPException(status_code=400, detail="You are not a team manager, championship not found, or already registered")
    return result

@app.post("/races", status_code=201)
def add_race(championship_id:int=Body(), name:str=Body(), location:str=Body(), race_date:date=Body(), token=Header(None)):
    authorize(token, ["organizer"]) # changed: replaced manual token & role check with authorize
    return functions.schedule_race(championship_id=championship_id, name=name, location=location, race_date=race_date)

@app.get("/championships/{championship_id}/races")
def list_races(championship_id:int):
    result = functions.get_races(championship_id)
    if result is False:
        raise HTTPException(status_code=404, detail="Championship not found")
    return result


@app.post("/results", status_code=201)
def add_results(race_id:int=Body(), results:list=Body(), token=Header(None)):
    authorize(token, ["organizer"]) # changed: replaced manual token & role check with authorize
    result = functions.submit_results(race_id=race_id, results=results)
    if not result:
        raise HTTPException(status_code=400, detail="Race not found, or a driver is not accepted or not registered in this championship")
    return result


@app.get("/standings")
def get_standings(championship_id: int):
    result = functions.get_standings(championship_id)
    if result is False:
        raise HTTPException(status_code=404, detail="Championship not found")
    return result

@app.get("/driver-history")
def get_driver_history(driver_id: int):
    result = functions.get_driver_history(driver_id)
    if not result:
        raise HTTPException(status_code=404, detail="Driver not found")
    return result