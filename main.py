import socket
from flask import Flask, render_template_string
import os

app = Flask(__name__)

# YOUR TUNNEL INFO
TARGET_URL = "while-seen.gl.at.ply.gg"
TARGET_PORT = 9282

def get_bo2_data():
    # The standard 'getinfo' heartbeat for BO2/Plutonium
    MESSAGE = b'\xff\xff\xff\xffgetinfo\x0a'
    try:
        ip = socket.gethostbyname(TARGET_URL)
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.settimeout(2.5)
        
        sock.sendto(MESSAGE, (ip, TARGET_PORT))
        data, addr = sock.recvfrom(2048)
        sock.close()

        # Parse Quake engine string (\hostname\MyServer\mapname\mp_nuketown...)
        decoded = data.decode('latin-1').split('\\')
        stats = {}
        for i in range(1, len(decoded), 2):
            stats[decoded[i]] = decoded[i+1] if i+1 < len(decoded) else ""
            
        return {
            "online": True,
            "name": stats.get("sv_hostname", "BO2 Server"),
            "map": stats.get("mapname", "Unknown"),
            "clients": stats.get("clients", "0"),
            "max": stats.get("sv_maxclients", "18")
        }
    except:
        return {"online": False}

@app.route('/')
def home():
    data = get_bo2_data()
    status_color = "#00ff00" if data["online"] else "#ff4444"
    
    return render_template_string('''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>BO2 Server Status</title>
        <style>
            body { background: #0a0a0a; color: white; font-family: sans-serif; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; }
            .card { background: #111; padding: 40px; border-radius: 20px; border: 1px solid #222; text-align: center; min-width: 300px; }
            .status { font-size: 50px; color: {{color}}; margin: 10px 0; font-weight: bold; }
            .map { color: #888; text-transform: uppercase; letter-spacing: 1px; }
            .players { font-size: 24px; margin: 20px 0; }
            .addr { font-family: monospace; color: #444; font-size: 12px; }
            button { background: #222; color: #888; border: 1px solid #333; padding: 10px; border-radius: 5px; cursor: pointer; margin-top: 20px; }
        </style>
    </head>
    <body>
        <div class="card">
            <div class="map">{{ data.get('name', 'SERVER') }}</div>
            <div class="status">{{ 'ONLINE' if data.online else 'OFFLINE' }}</div>
            {% if data.online %}
                <div class="map">MAP: {{ data.map }}</div>
                <div class="players">{{ data.clients }} / {{ data.max }} PLAYERS</div>
            {% endif %}
            <div class="addr">{{ url }}:{{ port }}</div>
            <button onclick="location.reload()">REFRESH</button>
        </div>
    </body>
    </html>
    ''', data=data, color=status_color, url=TARGET_URL, port=TARGET_PORT)

if __name__ == '__main__':
    # Koyeb assigns a port via environment variable, default to 8000
    port = int(os.environ.get("PORT", 8000))
    app.run(host='0.0.0.0', port=port)