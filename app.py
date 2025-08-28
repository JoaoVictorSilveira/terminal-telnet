from flask import Flask, request, jsonify, session, render_template
import telnetlib
import threading
import time
import uuid

app = Flask(__name__)
app.secret_key = "sua-chave-secreta"

# Sessões Telnet
telnet_sessions = {}
last_output = {}

def read_telnet_output(tn, telnet_id):
    while True:
        try:
            data = tn.read_very_eager().decode(errors="ignore")
            if data:
                last_output[telnet_id] += data
            time.sleep(0.2)
        except EOFError:
            break
        except Exception:
            break

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/connect_telnet', methods=['POST'])
def connect_telnet():
    data = request.get_json()
    ip = data.get("ip")
    port = int(data.get("port"))

    telnet_id = str(uuid.uuid4())
    try:
        tn = telnetlib.Telnet(ip, port, timeout=5)
        telnet_sessions[telnet_id] = tn
        last_output[telnet_id] = ""
        session['telnet_id'] = telnet_id

        threading.Thread(target=read_telnet_output, args=(tn, telnet_id), daemon=True).start()
        return jsonify({"message": f"Conectado ao Telnet {ip}:{port}"})
    except Exception as e:
        return jsonify({"message": f"Erro ao conectar: {e}"})

@app.route('/disconnect_telnet', methods=['POST'])
def disconnect_telnet():
    telnet_id = session.get('telnet_id')
    if telnet_id and telnet_id in telnet_sessions:
        try:
            tn = telnet_sessions[telnet_id]
            tn.close()
        except:
            pass
        del telnet_sessions[telnet_id]
        del last_output[telnet_id]

    session.pop('telnet_id', None)
    return jsonify({"message": "Telnet desconectado com sucesso!"})

@app.route('/send_command', methods=['POST'])
def send_command():
    telnet_id = session.get('telnet_id')
    if telnet_id not in telnet_sessions:
        return jsonify({"message": "Nenhuma sessão ativa."})

    tn = telnet_sessions[telnet_id]
    command = request.json.get("command")
    tn.write(command.encode("utf-8") + b"\n")
    return jsonify({"message": f"Comando enviado: {command}"})

@app.route('/get_output')
def get_output():
    telnet_id = session.get('telnet_id')
    if not telnet_id or telnet_id not in last_output:
        return jsonify({"output": ""})
    return jsonify({"output": last_output[telnet_id]})

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
