from flask import Flask, request, render_template, jsonify, session
import socket
import time

app = Flask(__name__)
app.secret_key = 'sua-chave-secreta'

# Dicionários para armazenar conexões Telnet e últimas respostas
telnet_sessions = {}
last_responses = {}

# Credenciais fixas para Telnet
TELNET_USERNAME = 'usuario'  # Coloque o nome de usuário fixo aqui
TELNET_PASSWORD = 'senha'    # Coloque a senha fixa aqui

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['POST'])
def login_telnet():
    try:
        # Recebendo os dados do formulário
        hostname = request.form['hostname']
        port = int(request.form['port'])

        # Configurando o socket Telnet
        telnet_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        telnet_socket.connect((hostname, port))

        # Realizando login com credenciais fixas
        telnet_socket.recv(1024)  # Aguarda mensagem inicial
        telnet_socket.sendall(f"{TELNET_USERNAME}\n".encode('ascii'))
        telnet_socket.recv(1024)  # Aguarda pedido de senha
        telnet_socket.sendall(f"{TELNET_PASSWORD}\n".encode('ascii'))

        # Salvando a conexão na sessão do Flask
        session_id = f"{hostname}:{port}"
        telnet_sessions[session_id] = telnet_socket
        last_responses[session_id] = ""  # Inicializa com saída vazia
        session['session_id'] = session_id

        return jsonify({"message": "Login realizado com sucesso.", "error": ""})
    except Exception as e:
        return jsonify({"error": str(e)})

@app.route('/execute_predefined', methods=['POST'])
def execute_predefined_commands():
    try:
        session_id = session.get('session_id')
        if not session_id or session_id not in telnet_sessions:
            return jsonify({"error": "Nenhuma sessão ativa. Faça login novamente."})

        telnet_socket = telnet_sessions[session_id]
        var1 = request.json.get('var1', '')
        var2 = request.json.get('var2', '')
        command_set = request.json.get('command_set')

        command_sets = {
            "login": ["intelbras", "intelbras"],
            "get_id": [f"onu inventory 1/{var1}", "yes"],
            "autoriza_ont": [f"onu set 1-1-{var1}-{var2} meprof intelbras-142ng",
                             f"bridge add 1-1-{var1}-{var2}/gpononu downlink vlan 110{var1} tagged rg"],
            "autoriza_onu": [f"onu set 1-1-{var1}-{var2} meprof intelbras-110g",
                             f"bridge add 1-1-{var1}-{var2}/gpononu downlink vlan 110{var1} tagged rg"],
            "delete_onu": [f"onu delete 1-1-{var1}-{var2}", "yes", "no", "yes"]
        }

        commands = command_sets.get(command_set)
        if not commands:
            return jsonify({"error": "Conjunto de comandos inválido."})

        # Substituir var2 somente se o comando necessitar dela
        output = ""
        for command in commands:
            command = command.replace("{var1}", var1)
            if "{var2}" in command:
                if not var2:
                    return jsonify({"error": "Variável 2 é obrigatória para este comando."})
                command = command.replace("{var2}", var2)

            telnet_socket.sendall(f"{command}\n".encode('ascii'))
            time.sleep(1)
            response = telnet_socket.recv(4096).decode('ascii')
            output += f"\n{response.strip()}"

        last_responses[session_id] = output
        return jsonify({"output": output.strip()})
    except Exception as e:
        return jsonify({"error": str(e)})

@app.route('/logout', methods=['POST'])
def logout_telnet():
    try:
        session_id = session.get('session_id')
        if session_id and session_id in telnet_sessions:
            telnet_sessions[session_id].close()
            del telnet_sessions[session_id]
            del last_responses[session_id]

        session.pop('session_id', None)
        return jsonify({"message": "Logout realizado com sucesso."})
    except Exception as e:
        return jsonify({"error": str(e)})

@app.route('/refresh_output', methods=['GET'])
def refresh_output():
    try:
        session_id = session.get('session_id')
        if not session_id or session_id not in last_responses:
            return jsonify({"error": "Nenhuma saída disponível. Execute um comando."})

        return jsonify({"output": last_responses[session_id], "error": ""})
    except Exception as e:
        return jsonify({"error": str(e)})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
