# core/arbitrage_strategy.py

import logging
import time

class ArbitrageStrategy:
    def __init__(self, config):
        self.config = config
        self.spread_entry = config['spread_entry']
        self.spread_exit = config['spread_exit']
        self.max_hold_time = config['max_hold_time']
        self.slippage_tolerance = config.get('slippage_tolerance', 0.002)
        self.symbol = config['symbol']
        self.start_time = None
        self.entry_data = None

    def calculate_spread(self, price_a, price_b):
        spread = price_a['mid'] - price_b['mid']
        logging.debug(f"Spread: {spread:.2f} = {price_a['mid']:.2f} - {price_b['mid']:.2f}")
        return spread

    def should_enter_trade(self, spread):
        return abs(spread) >= self.spread_entry

    def should_exit_trade(self, spread):
        time_held = time.time() - self.start_time if self.start_time else 0
        exit_due_to_spread = abs(spread) <= self.spread_exit
        exit_due_to_time = time_held >= self.max_hold_time
        if exit_due_to_spread:
            logging.info("Exiting trade: spread has converged.")
        if exit_due_to_time:
            logging.warning("Exiting trade: max hold time exceeded.")
        return exit_due_to_spread or exit_due_to_time

    def mark_entry(self, entry_spread, entry_prices):
        self.start_time = time.time()
        self.entry_data = {
            'spread': entry_spread,
            'prices': entry_prices,
            'time': self.start_time
        }
        logging.info(f"Entered trade at spread {entry_spread:.2f} with prices: {entry_prices}")

    def reset(self):
        self.start_time = None
        self.entry_data = None
