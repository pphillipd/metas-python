from flask import Flask, render_template, request, redirect
import json
from datetime import datetime

app = Flask(__name__)
ARQUIVO_JSON = 'tarefas.json'

# Função simples para ler os dados do arquivo
def carregar_tarefas():
    try:
        with open(ARQUIVO_JSON, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return []

# Função simples para salvar os dados no arquivo
def salvar_tarefas(tarefas):
    with open(ARQUIVO_JSON, 'w', encoding='utf-8') as f:
        json.dump(tarefas, f, indent=4, ensure_ascii=False)

# Rota principal (a página que você vai acessar no navegador)
@app.route('/', methods=['GET', 'POST'])
def index():
    tarefas = carregar_tarefas()
    
    # Se você enviou o formulário, salva a nova tarefa
    if request.method == 'POST':
        nova_tarefa = {
            'id': len(tarefas) + 1,
            'titulo': request.form['titulo'],
            'prazo': request.form['prazo']
        }
        tarefas.append(nova_tarefa)
        salvar_tarefas(tarefas)
        return redirect('/') # Recarrega a página para mostrar o novo prazo
    
    # Exibe a página com a lista de tarefas
    return render_template('index.html', tarefas=tarefas)

if __name__ == '__main__':
    # Roda o servidor localmente na porta 5000
    app.run(debug=True)

