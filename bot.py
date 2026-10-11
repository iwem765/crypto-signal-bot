import time
import requests
import datetime
import os

TELEGRAM_TOKEN = "8827909892:AAEknpOmleSykF8_GUIovzdRXx_BhP7uS_g"
BASE_URL = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"

COINS = {
    "Bitcoin": "BTCUSDT",
    "Ethereum": "ETHUSDT",
    "Solana": "SOLUSDT",
    "Ripple (XRP)": "XRPUSDT",
    "Cardano": "ADAUSDT",
    "Avalanche": "AVAXUSDT",
    "Dogecoin": "DOGEUSDT",
    "Binance Coin": "BNBUSDT",
    "Chainlink": "LINKUSDT",
    "Polygon": "POLUSDT"
}

previous_prices = {}
THRESHOLD_PERCENT = 0.005  
USERS_FILE = "users.txt"

def load_users():
    if not os.path.exists(USERS_FILE):
        return set()
    with open(USERS_FILE, "r", encoding="utf-8") as f:
        return set(line.strip() for line in f if line.strip().isdigit())

def send_telegram_message(chat_id, text):
    url = f"{BASE_URL}/sendMessage"
    payload = {"chat_id": chat_id, "text": text, "parse_mode": "Markdown"}
    try:
        r = requests.post(url, json=payload, timeout=10)
        if r.status_code == 200:
            print(f"  [✓] Успешно отправлено в Telegram для ID {chat_id}!")
            return True
        else:
            print(f"  [!] Ошибка API Telegram: {r.text}")
    except Exception as e:
        print(f"  [ОШИБКА сети]: {e}")
    return False

def main():
    print("=== ОБЛАЧНЫЙ ТОРГОВЫЙ БОТ ЗАПУЩЕН ===")
    
    users = load_users()
    print(f"[ИНФО]: Загружено клиентов из users.txt: {len(users)}")
    for uid in users:
        send_telegram_message(uid, "🔔 *Облачный узел активен! Бот круглосуточно мониторит рынок.*")

    global previous_prices
    while True:
        try:
            now = datetime.datetime.now().strftime("%H:%M:%S")
            print(f"\n[{now}] Анализ 10 монет...")
            
            for name, symbol in COINS.items():
                url = f"https://api.binance.com/api/v3/ticker/price?symbol={symbol}"
                response = requests.get(url, timeout=4)
                data = response.json()
                price = float(data.get('price', 0))
                
                if name in previous_prices:
                    old_price = previous_prices[name]
                    change = ((price - old_price) / old_price) * 100
                    
                    if abs(change) >= THRESHOLD_PERCENT:
                        direction = "🚀 ВВЕРХ" if change > 0 else "🔻 ВНИЗ"
                        msg = f"⚡ *СИГНАЛ РЫНКА* [{now}]\n\nАктив: *{name}*\nЦена: *${price:,.2f}*\nДвижение: *{direction} ({change:+.3f}%)*"
                        print(f"  [➔ СИГНАЛ]: {name} {change:+.3f}% -> Отправка")
                        
                        current_users = load_users()
                        for uid in current_users:
                            send_telegram_message(uid, msg)
                
                previous_prices[name] = price
                
        except Exception as e:
            print(f"[ОШИБКА цикла]: {e}")
            
        time.sleep(8)

if __name__ == "__main__":
    main()