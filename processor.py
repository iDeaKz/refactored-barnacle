# app/data/processor.py

from typing import Dict, List
import pandas as pd
import numpy as np
import logging
from app.config import Config


class DataProcessor:
    def __init__(self):
        pass

    def preprocess(self, raw_data: Dict[str, List[List[float]]]) -> Dict[str, pd.DataFrame]:
        processed_data = {}
        for key, ohlcv in raw_data.items():
            if not ohlcv:
                logging.warning(f"No data for {key}. Skipping preprocessing.")
                continue
            df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            df.set_index('timestamp', inplace=True)
            processed_data[key] = df
            logging.info(f"Preprocessed data for {key}.")
        return processed_data

    def feature_engineering(self, processed_data: Dict[str, pd.DataFrame], max_depth: int = 3) -> Dict[str, pd.DataFrame]:
        engineered_data = {}
        for key, df in processed_data.items():
            for depth in range(max_depth):
                df[f'ma_{depth}'] = df['close'].rolling(window=10 + depth * 5).mean()
                df[f'ema_{depth}'] = df['close'].ewm(span=10 + depth * 5, adjust=False).mean()
            df.dropna(inplace=True)
            engineered_data[key] = df
            logging.info(f"Engineered features for {key}.")
        return engineered_data
