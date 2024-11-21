# tests/test_processor.py

import pytest
import pandas as pd
from app.data.processor import DataProcessor


def test_preprocess(processor):
    raw_data = {
        'binance_BTC_USD': [
            [1609459200000, 29000, 29500, 28900, 29400, 500],
            [1609459260000, 29400, 29600, 29300, 29500, 600]
        ]
    }
    processed = processor.preprocess(raw_data)
    assert 'binance_BTC_USD' in processed, "Processed data should include binance_BTC_USD."
    df = processed['binance_BTC_USD']
    assert isinstance(df, pd.DataFrame), "Processed data should be a DataFrame."
    assert 'close' in df.columns, "DataFrame should contain 'close' column."
    assert df['close'].iloc[0] == 29400, "First close price should be 29400."


def test_feature_engineering(processor):
    raw_data = {
        'binance_BTC_USD': pd.DataFrame({
            'open': [29000, 29400, 29500, 29600, 29700],
            'high': [29500, 29600, 29700, 29800, 29900],
            'low': [28900, 29300, 29400, 29500, 29600],
            'close': [29400, 29500, 29600, 29700, 29800],
            'volume': [500, 600, 700, 800, 900]
        })
    }
    engineered = processor.feature_engineering(raw_data, max_depth=1)
    df = engineered['binance_BTC_USD']
    assert 'ma_0' in df.columns, "DataFrame should contain 'ma_0' column."
    assert 'ema_0' in df.columns, "DataFrame should contain 'ema_0' column."
