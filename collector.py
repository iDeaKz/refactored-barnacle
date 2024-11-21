# app/data/collector.py

import asyncio
from typing import Dict, List
import ccxt.async_support as ccxt
import logging


class DataCollector:
    def __init__(self, config):
        self.config = config
        self.exchanges = self.initialize_exchanges()

    def initialize_exchanges(self) -> Dict[str, ccxt.Exchange]:
        exchange_names = ['binance', 'coinbasepro']  # Add more as needed
        exchanges = {}
        for name in exchange_names:
            exchange_class = getattr(ccxt, name)
            exchanges[name] = exchange_class()
        logging.info("Exchanges initialized for data collection.")
        return exchanges

    async def fetch_data(self, exchange_name: str, symbol: str) -> List[List[float]]:
        exchange = self.exchanges.get(exchange_name)
        if not exchange:
            logging.error(f"Exchange '{exchange_name}' not supported.")
            return []
        try:
            ohlcv = await exchange.fetch_ohlcv(symbol, timeframe='1h')
            logging.info(f"Fetched data for {symbol} from {exchange_name}.")
            return ohlcv
        except Exception as e:
            logging.error(f"Error fetching data from {exchange_name} for {symbol}: {e}")
            return []

    async def collect_all_data(self) -> Dict[str, List[List[float]]]:
        tasks = []
        symbols = ['BTC/USD', 'ETH/USD']  # Extend symbols as needed
        for exchange_name in self.exchanges.keys():
            for symbol in symbols:
                tasks.append(self.fetch_data(exchange_name, symbol))
        results = await asyncio.gather(*tasks, return_exceptions=True)
        data = {}
        for idx, result in enumerate(results):
            exchange_idx = idx // len(symbols)
            symbol_idx = idx % len(symbols)
            exchange_name = list(self.exchanges.keys())[exchange_idx]
            symbol = symbols[symbol_idx]
            key = f"{exchange_name}_{symbol.replace('/', '_')}"
            if isinstance(result, list):
                data[key] = result
            else:
                logging.error(f"Failed to fetch data for {key}: {result}")
                data[key] = []
        return data

    async def close_exchanges(self):
        for exchange in self.exchanges.values():
            await exchange.close()
        logging.info("All exchange connections closed.")
