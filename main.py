# main.py

import asyncio
import signal
import logging
from configparser import ConfigParser

from exchanges.binance_client import BinanceClient
from exchanges.bybit_client import BybitClient
from strategy.arbitrage_strategy import ArbitrageStrategy
from core.trade_executor import TradeExecutor
from core.logger import setup_logger

CONFIG_FILE = "config/settings.ini"

# Graceful shutdown handler
shutdown = False
def handle_shutdown(signum, frame):
    global shutdown
    print("Shutdown signal received...")
    shutdown = True

# Register signals
signal.signal(signal.SIGINT, handle_shutdown)
signal.signal(signal.SIGTERM, handle_shutdown)

async def main():
    # Load config
    config = ConfigParser()
    config.read(CONFIG_FILE)
    settings = config['DEFAULT']

    # Setup logging
    setup_logger(settings.get("log_level", "INFO"))

    symbol = settings["symbol"]
    spread_entry = float(settings["spread_entry"])
    spread_exit = float(settings["spread_exit"])
    amount = float(settings["amount"])
    poll_interval = float(settings["poll_interval"])
    max_hold_time = int(settings["max_hold_time"])
    slippage_tolerance = float(settings["slippage_tolerance"])
    dry_run = settings.getboolean("use_dry_run", fallback=True)

    # Initialize exchanges
    binance = BinanceClient(settings, dry_run=dry_run)
    bybit = BybitClient(settings, dry_run=dry_run)

    # Initialize strategy and executor
    strategy = ArbitrageStrategy(
        exchange_a=binance,
        exchange_b=bybit,
        symbol=symbol,
        spread_entry=spread_entry,
        spread_exit=spread_exit,
        slippage_tolerance=slippage_tolerance,
    )
    executor = TradeExecutor(
        exchange_a=binance,
        exchange_b=bybit,
        symbol=symbol,
        amount=amount,
        max_hold_time=max_hold_time,
        dry_run=dry_run
    )

    print("🔁 Starting arbitrage loop...")
    while not shutdown:
        try:
            signal = await strategy.check_opportunity()
            if signal:
                await executor.execute(signal)
        except Exception as e:
            logging.exception(f"❌ Error in main loop: {e}")
        await asyncio.sleep(poll_interval)

    print("🛑 Shutting down...")

if __name__ == "__main__":
    asyncio.run(main())
