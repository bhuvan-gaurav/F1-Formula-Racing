from fastapi import FastAPI, HTTPException, Header, Body
import functions

app = FastAPI()


@app.post("/organizers")
def creating_organizer(user_name=Body(), password=Body(), token=Header(None)):
    username = functions.verify_token(token, "access")
    if not username:
        raise HTTPException(status_code=401, detail="Invalid token")
    if functions.get_role(username) != "admin":
        raise HTTPException(status_code=403, detail="Only admin allowed")
    result = functions.create_organizer(user_name, password)
    if not result:
        raise HTTPException(status_code=409, detail="User already exists")
    return result


@app.post("/teams")
def creating_team(name: str, country: str, manager_id: int, driver_limit: int, token=Header(None)):
    username = functions.verify_token(token, "access")
    if not username:
        raise HTTPException(status_code=401, detail="Invalid token")
    if functions.get_role(username) != "admin":
        raise HTTPException(status_code=403, detail="Only admin allowed")
    result = functions.create_team(name, country, manager_id, driver_limit)
    if not result:
        raise HTTPException(status_code=400, detail="Manager not found or team already exists")
    return result


@app.get("/teams")
def get_teams():
    return functions.get_teams()


@app.get("/standings")
def get_standings(championship_id: int):
    result = functions.get_standings(championship_id)
    if not result:
        raise HTTPException(status_code=404, detail="Championship not found")
    return result


@app.get("/driver-history")
def get_driver_history(driver_id: int):
    result = functions.get_driver_history(driver_id)
    if not result:
        raise HTTPException(status_code=404, detail="Driver not found")
    return result
