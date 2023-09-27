# Importando as bibliotecas necessárias
from flask import Flask, render_template, request, redirect, flash
from apscheduler.schedulers.background import BackgroundScheduler
import datetime
from data import get_db_connection, Boletos, Config
from helpers import notificacao_email
from datetime import datetime

app = Flask(__name__)

@app.route('/')
def index():
    conn = get_db_connection()
    email = conn.query(Config).first()
    if email == None:
        print('No email address')
        return render_template('configuracoes.html', email=False)
    

    conn = get_db_connection()
    boletos = conn.query(Boletos).all()
    conn.close()

    boletos_view = []
    soma = []

    for b in boletos:
        if b.sit_pagamento == False:
            boletos_view.append(b)
            soma.append(b.valor)

    return render_template('index.html', boletos=boletos_view, valorTotal=sum(soma))
# Rota 2 - cadastrar um novo boleto
@app.route('/cadastrar', methods=['GET', 'POST'])
def cadastrar_boleto():
    if request.method == 'POST':
        nome = request.form['nome']
        valor = request.form['valor']
        venc = request.form['vencimento']
        aler = request.form['alerta_email']

        vencimento = datetime.strptime(venc, '%Y-%m-%d').date()
        alerta_email = datetime.strptime(aler, '%Y-%m-%d').date()

        conn = get_db_connection()
        novo_boleto = Boletos(nome=nome, valor=valor, vencimento=vencimento, alerta_email=alerta_email)
        conn.add(novo_boleto)
        conn.commit()
        conn.close()

        return redirect('/')

    return render_template('adicionar_boleto.html')
# Rota 3 - pagar boleto
@app.route('/pagar/<int:id>', methods=['GET', 'POST'])
def pagar_boleto(id):
    conn = get_db_connection()
    boleto = conn.query(Boletos).get(id)
    boleto.sit_pagamento = True
    conn.commit()
    conn.close()

    return redirect('/')
# Rota para Boletos pagos
@app.route('/boletos_pagos')
def boletos_pagos():
    conn = get_db_connection()
    boletos = conn.query(Boletos).all()
    conn.close()

    boletos_pgs = []
    for b in boletos:
        if b.sit_pagamento == True:
            boletos_pgs.append(b)

    return render_template('boletos_pagos.html', boletos=boletos_pgs)

# Rota para excluir um boleto existente
@app.route('/excluir/<int:id>', methods=['GET', 'POST'])
def excluir_boleto(id):
    conn = get_db_connection()

    boleto = conn.query(Boletos).get(id)
    conn.delete(boleto)
    conn.commit()
    conn.close()

    return redirect('/')
# Rota para editar um boleto existente
@app.route('/editar/<int:id>', methods=['GET', 'POST'])
def editar_boleto(id):
    conn = get_db_connection()
    boleto = conn.query(Boletos).filter(Boletos.id == id).first()
    conn.close()

    if request.method == 'POST':
        nome = request.form['nome']
        valor = request.form['valor']
        venc = request.form['vencimento']
        aler = request.form['alerta_email']

        conn = get_db_connection()
        boleto = conn.query(Boletos).filter(Boletos.id == id).first()
        boleto.nome = nome
        boleto.valor = valor

        vencimento = datetime.strptime(venc, '%Y-%m-%d').date()
        alerta_email = datetime.strptime(aler, '%Y-%m-%d').date()

        boleto.vencimento = vencimento
        boleto.alerta_email = alerta_email
        conn.commit()
        conn.close()

        return redirect('/')

    return render_template('editar.html', boleto=boleto)
# Rota para adcionar o email (deve ser a primeira tela executada)





@app.route('/configuracoes', methods=['POST'])
def configuracoes():
    conn = get_db_connection()
    email = conn.query(Config).first()
    if email == None:
        return render_template('configuracoes.html', email=False)

    conn = get_db_connection()
    email = conn.query(Config).first()
    conn.close

    if request.method == 'POST':
        email = request.form['email']
        print('email: ', email)
        if not email:
            print('O campo de e-mail não pode estar vazio!')
        else:
            conn = get_db_connection()
            new_email = conn.query(Config).first()
            new_email.email = email
            conn.commit()
            conn.close()
            print('Configuração de e-mail atualizada com sucesso')

            return redirect('/')

    return render_template('configuracoes.html', email=email)
# Funcao para mandar notificacoes
def verifica_banco():
    print('lendo banco ... ')
    pass
    # raspa o banco se data de atual = data de vencimento
        # manda notificacao para email BOLETO VENCE HOJE
    

# Inicializando o aplicativo Flask
if __name__ == '__main__':

    scheduler = BackgroundScheduler()
    scheduler.add_job(verifica_banco, 'interval', seconds=60)  # Executar a verificação 
    scheduler.start()

    app.run(debug=True)