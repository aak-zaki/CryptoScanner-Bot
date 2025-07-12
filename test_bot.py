from config import BOT_TOKEN, CHAT_ID
import requests

url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
data = {"chat_id": CHAT_ID, "text": "Test bot berhasil kirim dari VPS!"}
resp = requests.post(url, data=data)
print(resp.status_code, resp.text)
