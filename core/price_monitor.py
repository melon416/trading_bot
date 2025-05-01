# core/price_monitor.py

import time
import logging

class PriceMonitor:
    def __init__(self, client_a, client_b, symbol, poll_interval=1):
        self.client_a = client_a
        self.client_b = client_b
        self.symbol = symbol
        self.poll_interval = poll_interval

    def get_prices(self):
        price_a = self.client_a.get_mid_price(self.symbol)
        price_b = self.client_b.get_mid_price(self.symbol)
        return price_a, price_b

    def calculate_spread(self, price_a, price_b):
        return price_a - price_b

    def monitor_loop(self):
        logging.info(f"Starting price monitor for {self.symbol}...")
        while True:
            try:
                price_a, price_b = self.get_prices()

                if price_a is None or price_b is None:
                    logging.warning("Failed to fetch one or both prices. Retrying...")
                    time.sleep(self.poll_interval)
                    continue

                spread = self.calculate_spread(price_a, price_b)
                logging.info(f"[{self.symbol}] Price A: {price_a:.2f} | Price B: {price_b:.2f} | Spread: {spread:.2f}")

                time.sleep(self.poll_interval)

            except Exception as e:
                logging.exception("Error during price monitoring loop")
                time.sleep(self.poll_interval)
