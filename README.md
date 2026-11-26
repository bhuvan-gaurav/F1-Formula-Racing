# F1 Formula Racing Championship Manager

A FastAPI backend for managing a Formula racing championship. It supports user accounts and role-based access for administrators, organizers, drivers, and team managers, along with teams, race schedules, results, standings, and driver history.

## Features

- User registration and login with Argon2 password hashing
- Short-lived JWT access tokens and refresh tokens
- Admin-managed team and organizer accounts
- Driver profiles and team applications with manager approval
- Championship creation, team registration, and race scheduling
- Race result submission with automatic points allocation
- Championship standings and driver race history
- SQLite persistence through SQLAlchemy
- Interactive API documentation provided by FastAPI

## Technology

- Python
- FastAPI
- SQLAlchemy
- SQLite
- PyJWT
- Argon2

## Project files

The application code is organized into an API module and a database/business-logic module:

```text
.
├── main.py        # FastAPI routes
├── functions.py   # SQLAlchemy models and application logic
├── requirements.txt
└── README.md
```

The SQLite database file (`FormulaRacing.db`) is created automatically when the database module is first loaded.

## Getting started

### 1. Clone the repository

```bash
git clone https://github.com/<your-username>/<your-repository>.git
cd <your-repository>
```

### 2. Create and activate a virtual environment

```bash
python -m venv .venv
```

macOS/Linux:

```bash
source .venv/bin/activate
```

Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

### 3. Install dependencies

Create a `requirements.txt` containing:

```text
fastapi
uvicorn[standard]
sqlalchemy
PyJWT
argon2-cffi
```

Then install them:

```bash
pip install -r requirements.txt
```

### 4. Start the API

```bash
uvicorn main:app --reload
```

By default, the API is available at `http://127.0.0.1:8000`.

## API documentation

With the server running, open:

- Swagger UI: `http://127.0.0.1:8000/docs`
  

## API overview

| Method | Endpoint | Purpose |
| --- | --- | --- |
| `POST` | `/register` | Register a user account (driver role by default) |
| `POST` | `/login` | Log in and receive access and refresh tokens |
| `POST` | `/refresh` | Exchange a refresh token for a new access token |
| `POST` | `/organizers` | Create an organizer account (admin only) |
| `POST` | `/teams` | Create a team (admin only) |
| `GET` | `/teams` | List teams and accepted driver counts |
| `GET` | `/teams/{team_id}` | Get team details |
| `POST` | `/Drivers` | Create a driver profile |
| `POST` | `/drivers/apply` | Apply to join a team |
| `PATCH` | `/applications` | Accept or reject a driver application |
| `POST` | `/championships` | Create a championship (organizer only) |
| `GET` | `/championships` | List championships |
| `POST` | `/championships/register` | Register a manager's team for a championship |
| `POST` | `/races` | Schedule a championship race (organizer only) |
| `GET` | `/championships/{championship_id}/races` | List races in a championship |
| `POST` | `/results` | Submit race results (organizer only) |
| `GET` | `/standings?championship_id={id}` | Get championship driver standings |
| `GET` | `/driver-history?driver_id={id}` | Get a driver's results and points total |

Endpoints that require authentication accept the access token in the `token` request header. The refresh endpoint accepts the refresh token in the `refresh_token` header.

## Points system

The application awards points to the top ten finishers:

| Position | Points | Position | Points |
| ---: | ---: | ---: | ---: |
| 1 | 25 | 6 | 8 |
| 2 | 18 | 7 | 6 |
| 3 | 15 | 8 | 4 |
| 4 | 12 | 9 | 2 |
| 5 | 10 | 10 | 1 |

Positions outside the top ten receive zero points.

## Initial administrator

On first database initialization, the code creates an administrator account with these development credentials:

```text
Username: admin
Password: Admin@123
```

Change this behavior and use environment variables or a secrets manager for credentials and JWT signing keys before deploying publicly. Do not commit real secrets or production database files to GitHub.

## Notes

- The API source currently defines the driver profile route as `/Drivers🏎️`; clients must use that exact path unless it is changed in the application.
- Keep the module names consistent with the startup command (`main.py` imports `functions.py`).
- Consider adding input validation, database migrations, automated tests, and production configuration as the project grows.
