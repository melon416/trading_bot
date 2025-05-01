# core/trade_executor.py

import logging
import time

class TradeExecutor:
    def __init__(self, client_a, client_b, config):
        self.client_a = client_a
        self.client_b = client_b
        self.symbol = config['symbol']
        self.amount = config['amount']
        self.slippage_tolerance = config.get('slippage_tolerance', 0.002)
        self.max_entry_time = config.get('max_entry_time', 5)

    def execute_entry(self, spread):
        # Decide direction based on spread
        if spread > 0:
            long_client, short_client = self.client_b, self.client_a
        else:
            long_client, short_client = self.client_a, self.client_b

        try:
            logging.info("Placing long and short positions...")
            t0 = time.time()

            # Place long order first
            long_order = long_client.place_order(self.symbol, 'long', self.amount)
            if not long_order['filled']:
                logging.error("Long order failed or not filled.")
                return False

            elapsed = time.time() - t0
            if elapsed > self.max_entry_time:
                logging.warning("Entry delayed: too much time passed after first order.")
                long_client.close_position(self.symbol, 'long')
                return False

            # Place short order second
            short_order = short_client.place_order(self.symbol, 'short', self.amount)
            if not short_order['filled']:
                logging.error("Short order failed or not filled. Reversing long...")
                long_client.close_position(self.symbol, 'long')
                return False

            logging.info("Both positions opened successfully.")
            return {
                'long_exchange': long_client.name,
                'short_exchange': short_client.name,
                'long_price': long_order['price'],
                'short_price': short_order['price']
            }

        except Exception as e:
            logging.exception(f"Error during trade entry: {e}")
            return False

    def execute_exit(self):
        try:
            logging.info("Closing both positions...")

            result_a = self.client_a.close_all_positions(self.symbol)
            result_b = self.client_b.close_all_positions(self.symbol)

            logging.info(f"Closed positions on {self.client_a.name} and {self.client_b.name}")
            return {
                'client_a': result_a,
                'client_b': result_b
            }

        except Exception as e:
            logging.exception("Error during trade exit.")
            return False
