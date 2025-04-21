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
class PredictionRequest(BaseModel):
    history: str
    bankroll: float

@app.post("/predict")
async def predict(request: PredictionRequest):
    history = request.history
    bankroll = request.bankroll

    # --- Your prediction logic here ---
    predictions = [1.5, 2.0, 1.8, 2.5, 1.1, 1.05, 3.2, 2.2, 1.7, 2.8]
    strategy = {
        "low_risk": {"bet": 1.5, "stake": bankroll * 0.6},
        "high_risk": {"bet": 2.8, "stake": bankroll * 0.4}
    }

    return {"predictions": predictions, "strategy": strategy}
