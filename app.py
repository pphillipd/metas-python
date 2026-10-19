from flask import Flask, render_template, request, redirect
import json
from datetime import datetime
import requests
from apscheduler.schedulers.background import BackgroundScheduler
import atexit

app = Flask(__name__)
ARQUIVO_JSON = 'tarefas.json'

# --- CONFIGURAÇÕES DO TELEGRAM ---
TELEGRAM_TOKEN = '8762894477:AAEojo_GclP8Ktr9lY9qv2VKnU9a81rGTm4'
TELEGRAM_CHAT_ID = '804908740'

def carregar_tarefas():
    try:
        with open(ARQUIVO_JSON, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return []

def salvar_tarefas(tarefas):
    with open(ARQUIVO_JSON, 'w', encoding='utf-8') as f:
        json.dump(tarefas, f, indent=4, ensure_ascii=False)
def enviar_mensagem_telegram(mensagem):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": mensagem}
    try:
        resposta = requests.post(url, data=payload)
        # Esta linha obriga o servidor a mostrar o que o Telegram respondeu
        print(f"\n[!] RESPOSTA DO TELEGRAM: {resposta.text}")
    except Exception as e:
        print(f"Erro de rede: {e}")

# --- O CRONÓMETRO INVISÍVEL (Agora mais inteligente) ---
def monitor_de_prazos():
    print("\n[*] O cronómetro acordou e está a verificar os prazos...")
    tarefas = carregar_tarefas()
    agora = datetime.now()
    atualizou = False

    for t in tarefas:
        if t.get('notificado', False):
            continue
        
        try:
            prazo = datetime.strptime(t['prazo'], '%Y-%m-%dT%H:%M')
            diferenca = prazo - agora
            horas = diferenca.total_seconds() / 3600
            
            print(f" -> Analisando: '{t['titulo']}' | Faltam {horas:.2f} horas")
            
            if 0 <= diferenca.total_seconds() <= 86400:
                mensagem = f"⏳ ALERTA DE PRAZO!\n\nTarefa: {t['titulo']}\nTempo restante: {round(horas, 1)} horas."
                enviar_mensagem_telegram(mensagem)
                print(" -> MENSAGEM ENVIADA AO TELEGRAM COM SUCESSO!")
                
                t['notificado'] = True
                atualizou = True
            else:
                print(" -> Nao foi enviada: O prazo ou ja passou ou falta mais de 24h.")
                
        except Exception as e:
             print(f" -> Erro ao ler a data da tarefa {t['titulo']}: {e}")
    
    if atualizou:
        salvar_tarefas(tarefas)

# Configurar o Agendador (Scheduler)
scheduler = BackgroundScheduler(timezone="America/Fortaleza")
# Define que a função vai correr a cada 1 minuto (pode alterar para 'minutes=60' depois)
scheduler.add_job(func=monitor_de_prazos, trigger="interval", minutes=1)
scheduler.start()

# Garante que o agendador desliga quando fechamos o servidor
atexit.register(lambda: scheduler.shutdown())


@app.route('/', methods=['GET', 'POST'])
def index():
    tarefas = carregar_tarefas()
    if request.method == 'POST':
        nova_tarefa = {
            'id': len(tarefas) + 1,
            'titulo': request.form['titulo'],
            'prazo': request.form['prazo'],
            'notificado': False
        }
        tarefas.append(nova_tarefa)
        salvar_tarefas(tarefas)
        return redirect('/')
    
    return render_template('index.html', tarefas=tarefas)

if __name__ == '__main__':
    # use_reloader=False é crucial quando se usa schedulers com o Flask
    app.run(host='0.0.0.0', port=5001, debug=True, use_reloader=False)

