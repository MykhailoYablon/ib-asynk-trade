import argparse
import time
from ib_async import IB
from ib_async.contract import Stock

def fetch_data(ib: IB, symbol: str):
    print(f"== Requesting data for {symbol} ==")

    start = time.perf_counter()
    contract = Stock(symbol, "SMART", "USD")
    bars = ib.reqHistoricalData(
        contract,
        endDateTime="",
        durationStr="1 D",
        barSizeSetting="5 mins",
        whatToShow="TRADES",
        useRTH=True
    )

    print(f"=== Received {symbol} Bars ===")

    for bar in bars[-10:]:
        print(f"{bar.date} O={bar.open:.2f} H={bar.high:.2f} L={bar.low:.2f} C={bar.close:.2f} V={int(bar.volume)}")

    end = time.perf_counter()
    print(f"Finished fetching {symbol} in {end - start} seconds")


def main(symbols):
    ib = IB()
    ib.connect('127.0.0.1', 7497, clientId=1)
    start = time.perf_counter()
    print(symbols)

    for symbol in symbols:
        fetch_data(ib, symbol)

    end = time.perf_counter()

    print(f"Finished fetching {len(symbols)} symbols in {end - start:.2f} seconds")

    ib.disconnect()


# start program
if __name__ == "__main__":
    # Parse command line arguments
    p = argparse.ArgumentParser(description="Fetch 1-min bars for multiple symbols from IBKR")
    p.add_argument("symbols", nargs="+", help="One or more ticker symbols, e.g. AAPL MSFT TSLA")
    args = p.parse_args()

    main(args.symbols)

