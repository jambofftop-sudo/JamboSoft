import requests
from flask import Flask, render_template, request, jsonify
import json
import os

app = Flask(__name__)

# --- НАСТРОЙКИ ---
TOKEN = "8378070736:AAHrX9RNxzrzvuq-SMrRUUaiJqxUK-YceOA"
CHANNEL_ID = "@zhakebreinrot"
item_counter = 1 

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/send_anketa', methods=['POST'])
def send_anketa():
    global item_counter
    try:
        m_val = request.form.get('money_val')
        m_sym = request.form.get('money_sym')
        p_val = request.form.get('price_val')
        p_cur = request.form.get('price_cur')
        wa = request.form.get('whatsapp', '').replace('+', '').replace(' ', '').strip()
        file = request.files.get('photo')

        if not file:
            return jsonify({"status": "error", "message": "Фото не выбрано"})

        text = (
            f"<b>💎 ЛОТ #{item_counter} | ZHAKE BRAINROT</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"<b>🐋 ПРИБЫЛЬ БРЕЙНРОТА : +{m_val} {m_sym}/СЕК</b>\n"
            f"<b>💰 ЦЕНА БРЕЙНРОТА : {p_val} {p_cur}</b>\n\n"
            f"<b>Гарант — @Zhake_breinrot 🛡️</b>"
        )

        keyboard = {
            "inline_keyboard": [[
                {
                    "text": "КУПИТЬ БРЕЙНРОТ 🐯",
                    "url": f"https://wa.me/{wa}"
                }
            ]]
        }

        url = f"https://api.telegram.org/bot{TOKEN}/sendPhoto"
        photo_bytes = file.read()
        
        payload = {
            'chat_id': CHANNEL_ID, 
            'caption': text, 
            'parse_mode': 'HTML',
            'reply_markup': json.dumps(keyboard)
        }
        
        response = requests.post(url, data=payload, files={'photo': photo_bytes})
        
        if response.status_code == 200:
            res_id = item_counter
            item_counter += 1
            return jsonify({"status": "success", "id": res_id})
        else:
            return jsonify({"status": "error", "message": response.text})

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

if __name__ == '__main__':
    # На хостингах порт берется из переменной окружения PORT
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)