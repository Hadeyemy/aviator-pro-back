from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import random

app = FastAPI()

# CORS setup for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://aviator-pro-mu.vercel.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class PredictionRequest(BaseModel):
    history: str
    bankroll: float

class RoundResult(BaseModel):
    odds: float
    won: bool

# Simple function to predict the next round's odds (randomly for simplicity)
def predict_next_round(history):
    # Predict a random odds range for the next round (1.01 to 10)
    return round(random.uniform(1.01, 10.00), 2)

# Function to calculate bet size based on current bankroll (simple strategy)
def calculate_bet(bankroll, round_num):
    bet_fraction = 0.1  # Bet 10% of current bankroll
    return round(bankroll * bet_fraction, 2)

# Function to update bankroll after a round (based on win or loss)
def update_bankroll(bankroll, bet, odds, won):
    if won:
        bankroll += bet * (odds - 1)  # Profit from winning the bet
    else:
        bankroll -= bet  # Loss if the bet was wrong
    return round(bankroll, 2)

@app.post("/predict")
async def predict(request: PredictionRequest):
    history = request.history
    bankroll = request.bankroll

    # Predict next round's odds
    odds = predict_next_round(history)

    # Calculate bet size for the next round
    bet = calculate_bet(bankroll, len(history.split(',')))

    return {"predictions": {"odds": odds, "bet": bet}}

@app.post("/update")
async def update(request: RoundResult, history: str, bankroll: float):
    odds = request.odds
    won = request.won

    # Update bankroll after the round
    bet = calculate_bet(bankroll, len(history.split(',')))
    bankroll = update_bankroll(bankroll, bet, odds, won)

    # Add the result to history (you can improve this by using more detailed history)
    history += f",{odds}:{'win' if won else 'loss'}"

    return {"updated_bankroll": bankroll, "updated_history": history}
