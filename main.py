from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI()

# ✅ Add this CORS setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://aviator-pro-mu.vercel.app"],  # For full security, replace "*" with your Vercel domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
class PredictRequest(BaseModel):
    history: List[float]
    bankroll: float

@app.post("/predict")
def predict_rounds(req: PredictRequest):
    predictions = []
    results = []
    bankroll = req.bankroll

    for i in range(10):
        last_avg = sum(req.history[-10:]) / len(req.history[-10:])
        predicted = round(random.uniform(0.8, 1.2) * last_avg, 2)
        predictions.append(predicted)

        low_target = 1.10
        high_target = 2.00 if predicted > 1.6 else 1.50

        low_bet = round(bankroll * 0.06, 2)
        high_bet = round(bankroll * 0.04, 2)

        low_hit = predicted >= low_target
        high_hit = predicted >= high_target

        bankroll += low_bet * (low_target - 1) if low_hit else -low_bet
        bankroll += high_bet * (high_target - 1) if high_hit else -high_bet

        results.append({
            "low_risk": {"bet": low_bet, "target": low_target, "hit": low_hit},
            "high_risk": {"bet": high_bet, "target": high_target, "hit": high_hit},
            "bankroll": round(bankroll, 2)
        })

        req.history.append(predicted)

    return {
        "predictions": predictions,
        "results": results,
        "final_bankroll": round(bankroll, 2)
    }
