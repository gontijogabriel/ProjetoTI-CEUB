# Importando as bibliotecas necessárias
from flask import Flask, render_template, request, redirect, flash
from apscheduler.schedulers.background import BackgroundScheduler
import sqlite3
import datetime
from data import get_db_connection, Boletos, Config
from helpers import notificacao_email
import schedule

app = Flask(__name__)


@app.route('/')
def index():
    conn = get_db_connection()
    boletos = conn.query(Boletos).all()
    conn.close()

    boletos_view = []
    soma = []

    for b in boletos:
        if b.situacao_pagamento == None:
            boletos_view.append(b)
            soma.append(b.valor)

    return render_template('index.html', boletos=boletos_view, valorTotal=sum(soma))


# Rota 2 - cadastrar um novo boleto
@app.route('/cadastrar', methods=['GET', 'POST'])
def cadastrar_boleto():
    if request.method == 'POST':
        nome = request.form['nome']
        valor = request.form['valor']
        vencimento = request.form['vencimento']
        alerta_email = request.form['alerta_email']

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
    data_pagamento = datetime.datetime.now()

    conn = get_db_connection()
    boleto = conn.query(Boletos).get(id)
    boleto.situacao_pagamento = data_pagamento
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
        if b.situacao_pagamento != None:
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
        vencimento = request.form['vencimento']
        alerta_email = request.form['alerta_email']

        conn = get_db_connection()
        boleto = conn.query(Boletos).filter(Boletos.id == id).first()
        boleto.nome = nome
        boleto.valor = valor
        boleto.vencimento = vencimento
        boleto.alerta_email = alerta_email
        conn.commit()
        conn.close()

        return redirect('/')

    return render_template('editar.html', boleto=boleto)


@app.route('/add_email', methods=['GET', 'POST'])
def add_email():
    email = None  # Defina email como None fora do bloco if
    
    if request.method == 'POST':
        email = request.form['email']
        
        if not email:
            print('O campo de e-mail não pode estar vazio!')
    else:
        conn = get_db_connection()
        new_email = conn.query(Config).first()
        
        if email is not None:  # Verifique se email foi definido
            new_email.email = email
            conn.commit()
            conn.close()
            print('Configuração de e-mail atualizada com sucesso')
            return redirect('/configuracoes')
    
    return render_template('configuracoes.html', email=email)


@app.route('/configuracoes', methods=['GET', 'POST'])
def configuracoes():
    conn = get_db_connection()
    num_registros  = conn.query(Config).count() 
    conn.close()

    if num_registros == 0:
        print('E-mail não cadastrado ainda')    
        
        return redirect('/add_email')

    if request.method == 'POST':

        email = request.form['email']
        
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

    
    return render_template('configuracoes.html', config=num_registros)


# Funcao para mandar notificacoes
def verifica_banco():
    print('lendo banco ... ')
    pass
    # raspa o banco se data de atual = data de vencimento
        # manda notificacao para email BOLETO VENCE HOJE
    



# Inicializando o aplicativo Flask
if __name__ == '__main__':

    scheduler = BackgroundScheduler()
    scheduler.add_job(verifica_banco, 'interval', seconds=60)  # Executar a verificação todos os dias
    scheduler.start()

    app.run(debug=True)