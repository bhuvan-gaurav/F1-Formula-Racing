from fastapi import FastAPI, HTTPException, Header, Body
import functions
from datetime import date
from pydantic import BaseModel,Field

app = FastAPI()
