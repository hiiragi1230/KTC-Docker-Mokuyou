from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import requests, os

app = FastAPI()

origins = ["*"]  # 学習用なので全許可
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_methods=["*"],
    allow_headers=["*"],
)

API_KEY = os.getenv("RIOT_API_KEY")

@app.get("/mvp/{summoner_name}")
def get_mvp(summoner_name: str):
    # 以前のMVP判定コード
    summoner_url = f"https://jp1.api.riotgames.com/lol/summoner/v4/summoners/by-name/{summoner_name}?api_key={API_KEY}"
    summoner = requests.get(summoner_url).json()
    puuid = summoner["puuid"]

    matches_url = f"https://asia.api.riotgames.com/lol/match/v5/matches/by-puuid/{puuid}/ids?count=1&api_key={API_KEY}"
    matches = requests.get(matches_url).json()
    match_id = matches[0]

    match_url = f"https://asia.api.riotgames.com/lol/match/v5/matches/{match_id}?api_key={API_KEY}"
    match_data = requests.get(match_url).json()

    players = match_data["info"]["participants"]
    scores = []
    for p in players:
        score = p["kills"] + p["assists"] - p["deaths"]*0.5 + p["visionScore"]*0.1
        scores.append((p["summonerName"], score))
    
    mvp = max(scores, key=lambda x: x[1])
    return {"matchId": match_id, "mvp": mvp[0], "score": mvp[1]}