from fastapi import FastAPI
import pandas as pd
import ast, datetime

app = FastAPI()

games  = pd.read_csv("./data/csv/games_steam.csv")
reviews =  pd.read_csv("./data/csv/user_review.csv")

@app.get("/")
def init():
    return {"Documentation": "/docs"}