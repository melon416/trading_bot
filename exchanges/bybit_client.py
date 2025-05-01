# exchanges/bybit_client.py

import ccxt
import logging

class BybitClient:
    def __init__(self, config, dry_run=True):
        self.dry_run = dry_run
        self.exchange = ccxt.bybit({
            'apiKey': config['bybit_api_key'],
            'secret': config['bybit_api_secret'],
            'enableRateLimit': True,
            'options': {'defaultType': 'future'},  # Ensure we're on USDT perpetuals
        })

    async def get_price(self, symbol):
        try:
            ticker = self.exchange.fetch_ticker(symbol)
            return {
                'bid': ticker['bid'],
                'ask': ticker['ask'],
                'mid': (ticker['bid'] + ticker['ask']) / 2
            }
        except Exception as e:
            logging.exception(f"[Bybit] Failed to fetch price for {symbol}")
            return None

    async def place_order(self, symbol, side, amount, price=None):
        try:
            if self.dry_run:
                logging.info(f"[DRY-RUN] {side.upper()} {amount} {symbol} at {price}")
                return {'order_id': 'dry-run'}
            
            order_type = 'market' if price is None else 'limit'
            order = self.exchange.create_order(
                symbol=symbol,
                type=order_type,
                side=side,
                amount=amount,
                price=price if order_type == 'limit' else None
            )
            logging.info(f"[Bybit] {side.upper()} {amount} {symbol} filled.")
            return order
        except Exception as e:
            logging.exception(f"[Bybit] Failed to place {side} order on {symbol}")
            return None

    async def close_position(self, symbol):
        try:
            if self.dry_run:
                logging.info(f"[DRY-RUN] Close {symbol} position")
                return

            positions = self.exchange.fetch_positions([symbol])
            for pos in positions:
                amt = float(pos['contracts'])
                side = 'sell' if amt > 0 else 'buy'
                if amt != 0:
                    self.exchange.create_market_order(symbol, side, abs(amt))
                    logging.info(f"[Bybit] Closed {side} {amt} position on {symbol}")
        except Exception as e:
            logging.exception(f"[Bybit] Failed to close position for {symbol}")
