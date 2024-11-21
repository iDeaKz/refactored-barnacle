# app/models/predictor.py

from typing import Dict, Any
import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.models import Sequential, load_model
from tensorflow.keras.layers import LSTM, Dense
from tensorflow.keras.optimizers import Adam
import logging
from app.config import Config
import os


class PricePredictor:
    def __init__(self, config: Config):
        self.input_steps = config.model.input_steps
        self.forecast_steps = config.model.forecast_steps
        self.scaler = MinMaxScaler(feature_range=(0, 1))
        self.model = None
        self.model_path = "app/models/model.h5"

    def build_model(self):
        self.model = Sequential()
        self.model.add(LSTM(50, return_sequences=True, input_shape=(self.input_steps, 1)))
        self.model.add(LSTM(50))
        self.model.add(Dense(self.forecast_steps))
        self.model.compile(optimizer=Adam(learning_rate=0.001), loss='mean_squared_error')
        logging.info("Model built successfully.")

    def prepare_data(self, df: pd.DataFrame) -> Dict[str, Any]:
        data = df['close'].values.reshape(-1, 1)
        data = self.scaler.fit_transform(data)

        X, y = [], []
        for i in range(self.input_steps, len(data) - self.forecast_steps +1):
            X.append(data[i - self.input_steps:i, 0])
            y.append(data[i:i + self.forecast_steps, 0])
        X, y = np.array(X), np.array(y)
        X = np.reshape(X, (X.shape[0], X.shape[1], 1))
        logging.info("Data prepared for training/prediction.")
        return {'X': X, 'y': y}

    def train(self, X: np.ndarray, y: np.ndarray, epochs: int = 50, batch_size: int = 32) -> float:
        if not self.model:
            self.build_model()
        history = self.model.fit(X, y, epochs=epochs, batch_size=batch_size, verbose=0)
        final_loss = history.history['loss'][-1]
        logging.info(f"Model trained with final loss: {final_loss}")
        return final_loss

    def predict(self, input_data: np.ndarray) -> np.ndarray:
        if not self.model:
            raise ValueError("Model is not loaded.")
        predictions = self.model.predict(input_data)
        predictions = self.scaler.inverse_transform(predictions)
        logging.info("Prediction made successfully.")
        return predictions

    def save_model(self, path: str = None):
        if not self.model:
            raise ValueError("No model to save.")
        path = path or self.model_path
        self.model.save(path)
        logging.info(f"Model saved to {path}.")

    def load_model(self, path: str = None):
        path = path or self.model_path
        if not os.path.exists(path):
            raise FileNotFoundError(f"Model file not found at {path}.")
        self.model = load_model(path)
        logging.info(f"Model loaded from {path}.")
