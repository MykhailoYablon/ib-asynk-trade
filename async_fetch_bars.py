import argparse
import time
from ib_async import IB, RealTimeBar
from ib_async.contract import Stock
import asyncio

async def main(symbols):
    ib = IB()
    await ib.connectAsync("127.0.0.1", 7497, clientId=1)

    # 1. Create a list of tasks (coroutines), but don't run them yet.
    # This is like setting up all the chess boards.
    fetch_data_coroutines = [
        fetch_opening_range(ib, symbol) for symbol in symbols
    ]

    # 2. Run all tasks concurrently and wait for them all to complete.
    print(f"Fetching data for {len(symbols)} symbols: {', '.join(symbols)}")
    results = await asyncio.gather(*fetch_data_coroutines)

    print("\n=== Opening Ranges ===")

    monitors = []
    for result in results:
        symbol, high, low = result
        print(f"{symbol}: Opening High Range = {high:.2f} Low={low:.2f}")
        monitors.append(monitor_with_breakout(ib, symbol, high, handler=log_breakout))

    print("Starting real-time 5-sec monitors...\n")
    await asyncio.gather(*monitors)
    # 3. Clean up.
    ib.disconnect()

async def fetch_opening_range(ib: IB, symbol: str, opening_range_minutes: int = 15):
    print(f"== Requesting data for {symbol} ==")

    contract = Stock(symbol, "SMART", "USD")
    bars = await ib.reqHistoricalDataAsync(
        contract,
        endDateTime="",
        durationStr="1 D",
        barSizeSetting="5 mins",
        whatToShow="TRADES",
        useRTH=True
    )

    opening_range_bars = bars[:opening_range_minutes]

    print(f"== Opening range for {symbol} ==")
    for bar in opening_range_bars:
        print(bar)

    highs = [b.high for b in opening_range_bars]
    lows = [b.low for b in opening_range_bars]

    return symbol, max(highs), min(lows)

def log_breakout(ib, symbol, bar: RealTimeBar, opening_range_high: float):
    with open("breakouts.log", "a") as f:
        f.write(f"{bar.time} {symbol} broke out, closed at {bar.close}, which was above {opening_range_high}\n")

async def monitor_with_breakout(ib: IB, symbol: str, opening_range_high: float, handler=log_breakout):
    ticker = ib.reqHistoricalDataAsync(
        contract = Stock(symbol, "SMART", "USD"),
        endDateTime="",
        durationStr="1 D",
        barSizeSetting="5 mins",
        whatToShow="TRADES",
        useRTH=True
    )

    def on_bar(bars: list[RealTimeBar], hasNewBar: bool):
        last_bar = bars[-1]
        bar_number = len(bars) - 1
        print(f"[{bar_number:2d}] {symbol} {last_bar.time.strftime('%H:%M:%S')}  "
              f"O={last_bar.open_:.2f}  H={last_bar.high:.2f}  "
              f"L={last_bar.low:.2f}  C={last_bar.close:.2f}")
        if last_bar.close > opening_range_high:
            print(f"\nBREAKOUT {symbol} @ {last_bar.time.strftime('%H:%M:%S')} "
                  f"C={last_bar.close:.2f} above {opening_range_high}\n")
            handler(ib, symbol, last_bar, opening_range_high)
            # unsubscribe so it only fires once
            ticker.updateEvent -= on_bar
        
    # Overloaded += operator to emit events
    ticker.updateEvent += on_bar
    # keep this coroutine alive indefinitely
    await asyncio.Event().wait()

if __name__ == "__main__":
    p = argparse.ArgumentParser(description="Fetch bars for multiple symbols from IBKR")
    p.add_argument("symbols", nargs="+", help="One or more ticker symbols")
    args = p.parse_args()
    asyncio.run(main(args.symbols)) # <--- 4. Run the main async function