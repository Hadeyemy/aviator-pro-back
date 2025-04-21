from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import random
import pandas as pd
from sklearn.linear_model import LinearRegression
import numpy as np

app = FastAPI()

# CORS Configuration to allow Vercel frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://aviator-pro-mu.vercel.app"],  # Replace with your Vercel app domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Data structure to hold historical data for crash predictions
history_data = []  # This will be your database or list to store past predictions

# Define the prediction request
class PredictionRequest(BaseModel):
    bankroll: float

# Define the prediction response
class PredictionResponse(BaseModel):
    predicted_odd: float
    low_risk_bet: float
    high_risk_bet: float
    message: str

def train_model():
    """ Train the machine learning model """
    # Convert the historical data into a DataFrame for training
    if len(history_data) < 2:  # Ensure there is enough data to train
        return None

    df = pd.DataFrame(history_data)
    
    # Feature: The previous predicted odds (X), Target: The next round's odds (y)
    X = df[['predicted_odd']].values  # Features
    y = df['actual_odd'].values  # Target variable
    
    # Train a simple Linear Regression model
    model = LinearRegression()
    model.fit(X, y)
    
    return model

@app.post("/predict", response_model=PredictionResponse)
async def predict(request: PredictionRequest):
    bankroll = request.bankroll

    # --- Machine Learning Prediction ---
    model = train_model()
    
    # If there is no trained model yet, generate a random prediction (for the first round)
    if model is None:
        predicted_odd = random.uniform(1.01, 10.00)  # Random value between 1.01 and 10.00
    else:
        # Use the model to predict the next round's odds based on the previous round's odds
        last_prediction = history_data[-1]['predicted_odd'] if history_data else random.uniform(1.01, 10.00)
        predicted_odd = model.predict([[last_prediction]])[0]  # Predict the next round

    # --- Bankroll Management ---
    low_risk_bet = bankroll * 0.6  # Low-risk bet: 60% of bankroll
    high_risk_bet = bankroll * 0.4  # High-risk bet: 40% of bankroll

    # Save the prediction (we assume actual_odd is entered after the round is finished)
    history_data.append({
        "bankroll": bankroll,
        "predicted_odd": predicted_odd,
        "actual_odd": 0  # Placeholder, actual_odd will be updated after the round
    })

    # Constructing response
    message = f"Predicted odd for next round: {predicted_odd:.2f}. Your low-risk bet: ${low_risk_bet:.2f}, high-risk bet: ${high_risk_bet:.2f}."
    
    return {"predicted_odd": predicted_odd, "low_risk_bet": low_risk_bet, "high_risk_bet": high_risk_bet, "message": message}

@app.post("/update_result")
async def update_result(prediction_index: int, actual_odd: float):
    """ Endpoint to update the actual odd and retrain the model """
    if prediction_index < len(history_data):
        # Update the actual odd in the history
        history_data[prediction_index]['actual_odd'] = actual_odd
        
        # Retrain the model with the updated data
        model = train_model()
        
        return {"status": "success", "message": "Data updated and model retrained."}
    
    raise HTTPException(status_code=404, detail="Prediction index not found")

