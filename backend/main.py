from fastapi import FastAPI, HTTPException, Header, Body
import functions
from datetime import date
from pydantic import BaseModel,Field

app = FastAPI()


@app.post("/register")
def register_user(user_name=Body(), password=Body()):
    if functions.register_user(user_name=user_name, password=password):
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
    username = functions.verify_token(token=refresh_token, token_type="refresh")
    if not username:
        raise HTTPException(status_code=401, detail="Invalid or expired refresh token")
    access_token = functions.create_token(username=username, token_type="access")
    return {"access_token": access_token}



@app.post("/Drivers🏎️")
def register_driver(name:str=Body(), country:str=Body(), date_of_birth:date=Body(), experience_years:int=Body(), token=Header(None)):
    user = functions.get_current_user(token)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid or expired access token")
    if user.role != "driver":
        raise HTTPException(status_code=403, detail="Only drivers can create a profile")
    results=functions.reg_driver(user_id=user.user_id,name=name,country=country,date_of_birth=date_of_birth,experience_years=experience_years)
    return results

@app.post("/drivers/apply")
def apply_team(team_id:int=Body(), token=Header(None)):
    user = functions.get_current_user(token=token,token_type="access")
    if not user:
        raise HTTPException(status_code=401, detail="Invalid or expired access token")
    if user.role != "driver":
        raise HTTPException(status_code=403, detail="Only drivers can apply")
    return functions.apply_to_team(user_id=user.user_id, team_id=team_id)

@app.patch("/applications")
def decide(driver_id:int=Body(), decision:str=Body(), token=Header(None)):
    user = functions.get_current_user(token=token,token_type="access")
    if not user:
        raise HTTPException(status_code=401, detail="Invalid or expired access token")
    return functions.decide_application(user_id=user.user_id, driver_id=driver_id, decision=decision)

@app.post("/championships/register", status_code=201)
def register_team(championship_id:int=Body(), token=Header(None)):
    user = functions.get_current_user(token)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid or expired access token")
    return functions.register_team_for_championship(user_id=user.user_id, championship_id=championship_id)

@app.get("/teams/{team_id}")
def team_details(team_id:int):
    return functions.get_team_details(team_id)