import requests
import time
from config import BOT_TOKEN, CHAT_ID
from coins import COINS

def fetch_technical_indicators(symbol, interval='1h'):
    url = f"https://api.binance.com/api/v3/klines?symbol={symbol}&interval={interval}&limit=100"
    try:
        response = requests.get(url, timeout=10)
        data = response.json()
        closes = [float(candle[4]) for candle in data]

        if len(closes) < 20:
            return None

        rsi = calculate_rsi(closes)
        cci = calculate_cci(data)
        price = closes[-1]

        return {'rsi': rsi, 'cci': cci, 'price': price}

    except Exception as e:
        print(f"Error fetching data for {symbol}: {e}")
        return None

def calculate_rsi(closes, period=14):
    gains = []
    losses = []
    for i in range(1, period + 1):
        change = closes[-i] - closes[-i - 1]
        if change >= 0:
            gains.append(change)
        else:
            losses.append(abs(change))

    avg_gain = sum(gains) / period
    avg_loss = sum(losses) / period if losses else 0.0001
    rs = avg_gain / avg_loss
    return round(100 - (100 / (1 + rs)), 2)

def calculate_cci(data, period=20):
    typical_prices = [(float(c[2]) + float(c[3]) + float(c[4])) / 3 for c in data[-period:]]
    tp = typical_prices[-1]
    ma = sum(typical_prices) / period
    mean_deviation = sum([abs(tp_i - ma) for tp_i in typical_prices]) / period
    if mean_deviation == 0:
        return 0
    cci = (tp - ma) / (0.015 * mean_deviation)
    return round(cci, 2)

def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": message, "parse_mode": "HTML"}
    try:
        response = requests.post(url, data=payload, timeout=10)
        if response.status_code != 200:
            print("Telegram error:", response.text)
    except Exception as e:
        print("Telegram exception:", e)

def check_signals():
    for symbol in COINS:
        indicators = fetch_technical_indicators(symbol)
        if not indicators:
            continue

        rsi = indicators['rsi']
        cci = indicators['cci']
        price = indicators['price']
        signal = ""

        if rsi < 30 and cci < -100:
            signal = "BUY"
        elif rsi > 70 and cci > 100:
            signal = "SELL"

        if signal:
            message = (
                f"<b>{symbol}</b> - Signal <b>{signal}</b>\n"
                f"Price: <code>{price}</code>\n"
                f"RSI: <code>{rsi}</code>\n"
                f"CCI: <code>{cci}</code>\n"
                f"#CryptoScannerBot"
            )
            print(f"Sending {signal} signal for {symbol}")
            send_telegram_message(message)

