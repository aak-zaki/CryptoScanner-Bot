import requests
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
        print(f"Error fetching data for {symbol} at {interval}: {e}")
        return None

def calculate_rsi(closes, period=14):
    gains, losses = [], []
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
    intervals = ['15m', '1h']  # Bisa tambahkan '4h', '1d' dsb.
    for symbol in COINS:
        signals = []
        for interval in intervals:
            indicators = fetch_technical_indicators(symbol, interval=interval)
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
            signals.append((interval, signal, rsi, cci, price))

        valid_signals = [s[1] for s in signals if s[1]]
        if len(valid_signals) == len(intervals) and len(set(valid_signals)) == 1:
            final_signal = valid_signals[0]
            message = f"<b>{symbol}</b> - Signal <b>{final_signal}</b>\n"
            for interval, _, rsi, cci, price in signals:
                message += f"[{interval}] Price: <code>{price}</code>, RSI: <code>{rsi}</code>, CCI: <code>{cci}</code>\n"
            message += "#CryptoScannerBot"
            print(f"Sending {final_signal} signal for {symbol}")
            send_telegram_message(message)


