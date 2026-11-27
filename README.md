# F1 – Formula Racing Championship Manager

A FastAPI backend to manage a Formula 1-style racing championship. Admins manage organizers and teams, organizers schedule races and publish results, and users register as drivers, join teams and take part in championships. Standings are calculated automatically from published race results.

**Stack:** Python, FastAPI, Pydantic, SQLAlchemy, SQLite, JWT (access + refresh), Argon2 password hashing, Docker, AWS EC2, GitHub Actions


## 1. Project and Team

Members -Akshay Bhuvan  Jashan 


## 2. Live App

- API: `http://<EC2_PUBLIC_IP>:8001`
- Docs: `http://<EC2_PUBLIC_IP>:8001/docs`


## 3. How to Run

**Project files**
```
main.py          # FastAPI routes, request validation, role checks
functions.py     # database tables, login/token logic, business logic
FormulaRacing.db # SQLite database (created automatically on first run)
```

**Backend**
```bash
git clone https://github.com/<user>/<repo>.git
cd <repo>
python -m venv venv
 venv\Scripts\activate
uvicorn main:app --port 8000 --reload
```
Open `http://localhost:8000/docs`.


**Docker 
```bash
docker build -t f1-championship-manager .
mkdir -p data
docker run -d --name f1-api -p 8001:8001 -v $(pwd)/data:/app/data f1-championship-manager
```

## 4. API Contract

**Sending the token:** protected endpoints read the access token from a request header named `token`. The refresh endpoint reads the refresh token from a header named `refresh-token`.

**Roles:** `admin`, `organizer`, `driver`. New registrations are `driver` by default and only admins can create organizers. A team manager is the user set as `manager_id` of a team.

| # | Functionality | Method | Path | Access | Request body | Success |
|---|---|---|---|---|---|---|
| A1 | Register | POST | `/register` | Public | user_name, password | 200 |
| A2 | Login (access + refresh tokens) | POST | `/login` | Public | username, password | 200 |
| A3 | New access token | POST | `/refresh` | Public (refresh-token header) | – | 200 |
| E1 | Create organizer account | POST | `/organizers` | Admin | user_name, password | 201 |
| E2 | Create racing team | POST | `/teams` | Admin | name, country, manager_id, driver_limit | 201 |
| E3 | Get all teams | GET | `/teams` | All | – | 200 |
| E4 | Get team details | GET | `/teams/{team_id}` | All | – | 200 |
| E5 | Create championship | POST | `/championships` | Organizer | name | 201 |
| E6 | Get all championships | GET | `/championships` | All | – | 200 |
| E7 | Register driver profile | POST | `/drivers` | Driver | name, country, date_of_birth, experience_years | 201 |
| E8 | Apply to join a team | POST | `/drivers/apply` | Driver | team_id | 200 |
| E9 | Accept or reject application | PATCH | `/applications` | Team manager | driver_id, decision (`accepted` or `rejected`) | 200 |
| E10 | Register team for championship | POST | `/championships/register` | Team manager | championship_id | 201 |
| E11 | Schedule a race | POST | `/races` | Organizer | championship_id, name, location, race_date | 201 |
| E12 | Get races of a championship | GET | `/championships/{championship_id}/races` | All | – | 200 |
| E13 | Submit race results | POST | `/results` | Organizer | race_id, results (list of driver_id, position, fastest_lap optional) | 201 |
| E14 | Championship standings | GET | `/standings?championship_id=` | All | – | 200 |
| E15 | Driver performance history | GET | `/driver-history?driver_id=` | All | – | 200 |

**Scoring**

| Position | 1st | 2nd | 3rd | 4th | 5th | 6th | 7th | 8th | 9th | 10th |
|---|---|---|---|---|---|---|---|---|---|---|
| Points | 25 | 18 | 15 | 12 | 10 | 8 | 6 | 4 | 2 | 1 |

Positions 11 and below score 0. Standings add up each driver's points across all races in the championship, highest first.

**Business rules**
- A team has a name, country, team manager and a driver limit.
- A driver applies to a team and only that team's manager can accept or reject.
- A team cannot accept more drivers than its driver limit.
- A driver can only apply if they have no pending or accepted application, so they cannot be in more than one team.
- Only drivers accepted into a team that is registered for the championship can receive results.

**Error rules**

| Status | Meaning |
|---|---|
| 400 | Business rule broken (team full, not the team's manager, already applied, profile already exists) |
| 401 | Missing, invalid or expired token, wrong login |
| 403 | Wrong role for the endpoint |
| 404 | Team, championship or driver not found |
| 409 | Username already exists |
| 422 | Invalid request body |

## 5. Database (SQLite)

- **users:** user_id, user_name, password (hashed), role
- **teams:** id, name, country, manager_id, driver_limit
- **drivers:** id, user_id, name, country, date_of_birth, experience_years, team_id, application_status
- **championships:** id, name, organizer_id
- **championship_teams:** id, championship_id, team_id
- **races:** id, championship_id, name, location, race_date
- **race_results:** id, race_id, driver_id, position, points, fastest_lap

A driver's application is stored on the `drivers` row: `team_id` is the team applied to and `application_status` is `pending`, `accepted` or `rejected`.

## 6. Deployment and CI/CD

- Dockerfile runs the app on port 8001 and the image is pushed to Docker Hub.
- One AWS EC2 instance runs the container. The security group allows ports 22 (SSH) and 8001 (API).
- GitHub Actions (`.github/workflows/deploy.yml`) builds the image, pushes it to Docker Hub, connects to EC2 over SSH, pulls the latest image and replaces the running container.
- GitHub Secrets used: `DOCKERHUB_USERNAME`, `DOCKERHUB_TOKEN`, `EC2_HOST`, `EC2_USER`, `EC2_SSH_KEY`.

## 7. 3-Day Contribution Plan

### Day 1

| Member | Work |
|---|---|
| Akshay | E7,E8 |
| Bhuvan | E1,E2 |
| Jashan |E5,E6  |

### Day 2

| Member | Work |
|---|---|
| Akshay | E9,E10 |
| Bhuvan | E3,E14  |
| Jashan | E11,E12  |
 
### Day 3

| Member | Work |
|---|---|
| Akshay | E4|
| Bhuvan | E15 |
| Jashan | E13 |
