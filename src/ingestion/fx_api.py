import requests
import json
import os
from datetime import datetime, timedelta
from loguru import logger
from config.settings import settings

class FXFetcher:
    def __init__(self):
        self.api_key = settings.EXCHANGE_RATE_API_KEY
        self.base_currency = settings.BASE_CURRENCY
        self.target_currencies = settings.TARGET_CURRENCIES
        self.url = f"https://v6.exchangerate-api.com/v6/{self.api_key}/latest/{self.base_currency}"
        self.cache_path = settings.PROCESSED_DATA_PATH / "fx_cache.json"

    def get_rates(self):
        """
        Fetch exchange rates for the target currencies with 24h caching.
        """
        # 1. Check Cache
        cached_data = self._load_cache()
        if cached_data:
            logger.info("Using cached FX rates.")
            return cached_data

        # 2. API Call if no valid cache
        if self.api_key == "demo_key" or not self.api_key:
            logger.warning("No API key provided or demo key used. Returning mock rates.")
            return self._get_mock_rates()

        try:
            logger.info(f"Fetching FX rates from API for {self.base_currency}...")
            response = requests.get(self.url, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if data.get("result") == "success":
                all_rates = data.get("conversion_rates", {})
                filtered_rates = {curr: all_rates.get(curr) for curr in self.target_currencies}
                filtered_rates[self.base_currency] = 1.0
                
                self._save_cache(filtered_rates)
                logger.info(f"Successfully fetched and cached rates: {filtered_rates}")
                return filtered_rates
            else:
                logger.error(f"API returned error: {data.get('error-type')}")
                return self._get_mock_rates()
                
        except Exception as e:
            logger.error(f"FX API request failed: {e}. Falling back to mock data.")
            return self._get_mock_rates()

    def _load_cache(self):
        if not os.path.exists(self.cache_path):
            return None
        
        try:
            with open(self.cache_path, 'r') as f:
                cache = json.load(f)
                timestamp = datetime.fromisoformat(cache['timestamp'])
                if datetime.now() - timestamp < timedelta(hours=24):
                    return cache['rates']
        except Exception:
            pass
        return None

    def _save_cache(self, rates):
        try:
            os.makedirs(os.path.dirname(self.cache_path), exist_ok=True)
            with open(self.cache_path, 'w') as f:
                json.dump({
                    'timestamp': datetime.now().isoformat(),
                    'rates': rates
                }, f)
        except Exception as e:
            logger.warning(f"Failed to save FX cache: {e}")

    def _get_mock_rates(self):
        """Standard mock rates for development"""
        return {
            "GBP": 1.0, "USD": 1.27, "EUR": 1.16, "MAD": 12.85
        }
