## Overview

This project contains two simple Python scripts that demonstrate how to fetch historical and real‑time bars from Interactive Brokers (IBKR) using the `ib_async` library.

- `fetch_bars.py`: Fetches historical 5‑minute bars for one or more symbols and prints the last 10 bars.
- `async_fetch_bars.py`: Concurrently fetches each symbol’s opening range from historical data, then starts a real‑time 5‑second bar monitor to detect and log breakouts.

Both scripts assume IBKR TWS or IB Gateway is running locally and the API is enabled.

## Prerequisites

- **Python**: 3.12 recommended
- **IBKR TWS or IB Gateway**: Logged in and running on the same machine
- **IBKR API settings** in TWS/Gateway:
  - Enable `API` access: Configure > API Settings > check "Enable ActiveX and Socket Clients"
  - Socket port: Paper by default is `7497` (Live often `7496`)
  - Allow connections from `127.0.0.1` (localhost)
  - Optional: Add `127.0.0.1` to Trusted IPs

## Install

From the project directory:

```bash
pip install -r requirements.txt
```

If you see a `ModuleNotFoundError: No module named 'tzdata'`, install it explicitly:

```bash
pip install tzdata
```

## Scripts

### `fetch_bars.py` — Historical 5‑min bars

Fetches 1 day of 5‑minute historical bars for each symbol (RTH only) and prints the last 10 bars.

Usage:

```bash
python fetch_bars.py AAPL MSFT TSLA
```

What it does:
- Connects to IBKR on `127.0.0.1:7497` with `clientId=1`
- Requests `1 D` of historical `TRADES` with `barSizeSetting="5 mins"` and `useRTH=True`
- Prints the last 10 bars for each symbol

### `async_fetch_bars.py` — Opening range + real‑time breakout monitor

For each symbol, concurrently:
1) Fetches historical data and computes an "opening range" from the first 15 five‑minute bars (i.e., 75 minutes) by default.
2) Starts a real‑time 5‑second bar stream (RTH only). If the close exceeds the opening range high, a breakout is printed and logged.

Usage:

```bash
python async_fetch_bars.py AAPL NVDA META
```

Behavior:
- Connects via `connectAsync("127.0.0.1", 7497, clientId=1)`
- Historical request: `1 D`, `5 mins`, `TRADES`, `useRTH=True`
- Computes per‑symbol opening range high/low
- Subscribes to 5‑second real‑time bars; prints each bar and logs the first breakout to `breakouts.log`
- Runs until you stop it (Ctrl+C)

Log file:
- Breakouts are appended to `breakouts.log` in the project directory.

## Common adjustments

If needed, edit the scripts to customize:
- `port`: `7497` (paper) or `7496` (live)
- `clientId`: Set a different integer if you run multiple API clients
- `durationStr`: e.g., `2 D`, `1 W`
- `barSizeSetting`: e.g., `1 min`, `15 mins`
- `whatToShow`: e.g., `MIDPOINT`, `BID_ASK`
- `useRTH`: set to `False` to include pre/post market where supported

## Troubleshooting

- **tzdata error**: If you see `ModuleNotFoundError: No module named 'tzdata'`, run `pip install tzdata`.
- **Cannot connect**:
  - Confirm TWS/Gateway is open and logged in
  - Verify API is enabled and the socket port matches the script (`7497` or `7496`)
  - Check Windows Firewall permissions for TWS/Gateway
  - Ensure `clientId` is not colliding with another running client
- **No market data returned**:
  - Ensure your IBKR account has market data subscriptions for the requested instruments
  - Symbols are valid for the specified exchange/currency (scripts use `SMART`/`USD`)
  - RTH only: consider setting `useRTH=False` if you need pre/post data
- **Rate limits / pacing violations**:
  - Avoid requesting too many symbols or too frequent requests simultaneously
  - Stagger or batch queries as needed

## Examples

```bash
# Historical bars
python fetch_bars.py AAPL

# Async opening range and real‑time breakout monitor
python async_fetch_bars.py AAPL MSFT
```

## Notes

- These scripts are examples for learning and research. Use at your own risk.
- Interactive Brokers is a registered trademark of Interactive Brokers Group, Inc.
