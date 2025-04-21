from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, validator
from typing import List

app = FastAPI()

# Add CORS middleware to allow cross-origin requests from your Vercel frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://aviator-pro-mu.vercel.app"],  # Vercel app domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Define the request model to accept data from the frontend
class PredictionRequest(BaseModel):
    history: str
    bankroll: float

    # Validator to ensure bankroll is a positive number
    @validator("bankroll")
    def validate_bankroll(cls, value):
        if value <= 0:
            raise ValueError("Bankroll must be a positive number.")
        return value

# Define a class for the prediction response
class PredictionResponse(BaseModel):
    predictions: List[float]
    strategy: dict

@app.post("/predict", response_model=PredictionResponse)
async def predict(request: PredictionRequest):
    # Extract history and bankroll from the request
    history = request.history
    bankroll = request.bankroll

    # --- Here, you can implement the actual prediction logic or integrate your ML model ---
    predictions = [1.5, 2.0, 1.8, 2.5, 1.1, 1.05, 3.2, 2.2, 1.7, 2.8]  # Example predictions

    # Betting strategy based on bankroll
    strategy = {
        "low_risk": {"bet": 1.5, "stake": bankroll * 0.6},  # Low-risk bet: 60% of bankroll
        "high_risk": {"bet": 2.8, "stake": bankroll * 0.4}  # High-risk bet: 40% of bankroll
    }

    # Return the predictions and betting strategy
    return {"predictions": predictions, "strategy": strategy}

