
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
import random
import numpy as np

app = FastAPI()

# CORS setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request body model
class PredictRequest(BaseModel):
    history: str
    bankroll: float = 100.0

@app.post("/predict")
async def predict(data: PredictRequest):
    try:
        raw_values = [float(x.strip()) for x in data.history.split(",") if x.strip()]
        if len(raw_values) < 10:
            return {"error": "At least 10 past values required."}

        bankroll = data.bankroll

        mean_val = np.mean(raw_values[-20:])
        std_dev = np.std(raw_values[-20:])

        predictions = []
        for _ in range(10):
            noise = np.random.normal(0, std_dev * 0.25)
            prediction = max(1.01, mean_val + noise)
            predictions.append(round(prediction, 2))

        low_risk_target = 1.3
        high_risk_target = 2.5

        win_chance_low = min(0.95, np.sum(np.array(raw_values) >= low_risk_target) / len(raw_values))
        win_chance_high = min(0.65, np.sum(np.array(raw_values) >= high_risk_target) / len(raw_values))

        def kelly_criterion(p, b):
            if b == 0 or p == 0:
                return 0
            return max(0, (p * (b + 1) - 1) / b)

        stake_low = round(bankroll * kelly_criterion(win_chance_low, low_risk_target - 1), 2)
        stake_high = round(bankroll * kelly_criterion(win_chance_high, high_risk_target - 1), 2)

        strategy = {
            "low_risk": {
                "bet": low_risk_target,
                "stake": min(stake_low, bankroll * 0.6)
            },
            "high_risk": {
                "bet": high_risk_target,
                "stake": min(stake_high, bankroll * 0.4)
            }
        }

        return {
            "predictions": predictions,
            "strategy": strategy
        }

    except Exception as e:
        return {"error": str(e)}
