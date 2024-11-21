# tests/test_collector.py

import pytest
from unittest.mock import AsyncMock, patch
from app.data.collector import DataCollector


@pytest.mark.asyncio
async def test_fetch_data_success(collector):
    collector.exchanges = {
        'binance': AsyncMock()
    }
    collector.exchanges['binance'].fetch_ohlcv.return_value = [
        [1609459200000, 29000, 29500, 28900, 29400, 500]
    ]
    data = await collector.fetch_data('binance', 'BTC/USD')
    assert len(data) == 1, "Should fetch one data point."
    assert data[0][4] == 29400, "Close price should match."


@pytest.mark.asyncio
async def test_fetch_data_failure(collector):
    collector.exchanges = {
        'binance': AsyncMock()
    }
    collector.exchanges['binance'].fetch_ohlcv.side_effect = Exception("API Error")
    data = await collector.fetch_data('binance', 'BTC/USD')
    assert data == [], "Failed fetch should return empty list."


@pytest.mark.asyncio
async def test_collect_all_data(collector):
    collector.exchanges = {
        'binance': AsyncMock(),
        'coinbasepro': AsyncMock()
    }
    collector.exchanges['binance'].fetch_ohlcv.return_value = [
        [1609459200000, 29000, 29500, 28900, 29400, 500]
    ]
    collector.exchanges['coinbasepro'].fetch_ohlcv.return_value = [
        [1609459200000, 29100, 29600, 29000, 29500, 600]
    ]
    data = await collector.collect_all_data()
    assert 'binance_BTC_USD' in data, "Data should include binance_BTC_USD."
    assert 'coinbasepro_BTC_USD' in data, "Data should include coinbasepro_BTC_USD."
    assert len(data['binance_BTC_USD']) == 1, "Binance data should have one entry."
    assert len(data['coinbasepro_BTC_USD']) == 1, "CoinbasePro data should have one entry."
