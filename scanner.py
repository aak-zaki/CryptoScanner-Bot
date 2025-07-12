import requests
import pandas as pd
from coins import COINS
from indicators import calculate_rsi, calculate_cci
from notifier import send_telegram
from config import GATE_API_URL

def fetch_candles(symbol, interval='1h', limit=100):
    params = {
        'currency_pair': symbol.lower(),
        'interval': interval,
        'limit': limit
    }
    try:
        res = requests.get(GATE_API_URL, params=params, timeout=10)
        data = res.json()
        df = pd.DataFrame(data, columns=[
            'timestamp', 'volume', 'close', 'high', 'low', 'open'
        ]).astype(float)
        df = df.iloc[::-1]
        df['close'] = df['close'].astype(float)
        df['high'] = df['high'].astype(float)
        df['low'] = df['low'].astype(float)
        return df
    except Exception as e:
        print(f"Error fetching {symbol}: {e}")
        return None

def check_signals():
    for symbol in COINS:
        df = fetch_candles(symbol)
        if df is None or len(df) < 20:
            continue

        rsi = calculate_rsi(df['close']).iloc[-1]
        cci = calculate_cci(df).iloc[-1]

        if rsi < 30 and cci < -100:
            signal = f"<b>BUY Signal</b> 🔼\nCoin: <b>{symbol}</b>\nRSI: <b>{rsi:.2f}</b>\nCCI: <b>{cci:.2f}</b>"
            send_telegram(signal)
        elif rsi > 70 and cci > 100:
            signal = f"<b>SELL Signal</b> 🔽\nCoin: <b>{symbol}</b>\nRSI: <b>{rsi:.2f}</b>\nCCI: <b>{cci:.2f}</b>"
            send_telegram(signal)
