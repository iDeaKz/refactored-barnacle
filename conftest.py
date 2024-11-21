# tests/conftest.py

import pytest
from unittest.mock import AsyncMock, patch
from app.config import Config, load_config
from app.models.predictor import PricePredictor
from app.data.collector import DataCollector
from app.data.processor import DataProcessor


@pytest.fixture(scope="session")
def config():
    # Load a separate test configuration to isolate test environments
    return load_config("tests/config_test.yaml")


@pytest.fixture
def predictor(config):
    predictor = PricePredictor(config)
    predictor.model = None  # Mock model to prevent actual training
    predictor.scaler = None
    return predictor


@pytest.fixture
def collector(config):
    collector = DataCollector(config)
    collector.exchanges = {}  # Mock exchanges to prevent real API calls
    return collector


@pytest.fixture
def processor():
    return DataProcessor()
