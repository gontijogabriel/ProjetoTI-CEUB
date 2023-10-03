# Importando as bibliotecas necessárias
from flask import Flask, render_template, request, redirect, flash
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
from data import get_db_connection, Boletos, Config
from helpers import notificacao_email, emoji_alerta
from sqlalchemy import func, desc, asc
from errors import errors

app = Flask(__name__)
app.secret_key = 'qwerty'

@app.route('/')
def index():
    conn = get_db_connection()
    email = conn.query(Config).first()
    if email == None:
        print('No email address')
        return render_template('add_email.html')
    
    # Pega todos os emails cadastrados
    conn = get_db_connection()
    boletos = conn.query(Boletos).order_by(asc(Boletos.vencimento)).all()
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
    conn = get_db_connection()
    email = conn.query(Config).first()
    if email == None:
        print('No email address')
        return render_template('add_email.html')

    if request.method == 'POST':
        nome = request.form['nome']
        valor = request.form['valor']
        venc = request.form['vencimento']
        aler = request.form['alerta_email']
        

        vencimento = datetime.strptime(venc, '%Y-%m-%d').date()
        alerta_email = datetime.strptime(aler, '%Y-%m-%d').date()

        alerta = emoji_alerta(vencimento)

        conn = get_db_connection()
        novo_boleto = Boletos(nome=nome, valor=valor, vencimento=vencimento, alerta=alerta[1], alerta_email=alerta_email)
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
    email = conn.query(Config).first()
    if email == None:
        print('No email address')
        return render_template('add_email.html')

    conn = get_db_connection()
    boletos = conn.query(Boletos).all()
    conn.close()

    boletos_pgs = []
    for b in boletos:
        if b.sit_pagamento == True:
            boletos_pgs.append(b)

    conn = get_db_connection()
    sumBoletosPgs = conn.query(func.sum(Boletos.valor)).filter(Boletos.sit_pagamento == True).scalar()
    conn.close()

    return render_template('boletos_pagos.html', boletos=boletos_pgs, sum_boletos_pgs=sumBoletosPgs)

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
@app.route('/add_email', methods=['GET', 'POST'])
def add_email():

    if request.method == 'POST':
        email = request.form['email']
        print('email: ', email)
        if not email:
            print('O campo de e-mail não pode estar vazio!')
        else:
            conn = get_db_connection()
            new_email = Config(email=email)
            conn.add(new_email)
            conn.commit()
            conn.close()
            print('Configuração de e-mail atualizada com sucesso')

            return redirect('/')

# Rota Configuracoes
@app.route('/configuracoes', methods=['GET', 'POST'])
def configuracoes():
    try:
        conn = get_db_connection()
        new_email = conn.query(Config).first().email
        conn.close
    except:
        return render_template('add_email.html')
        


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

    return render_template('configuracoes.html', email=new_email)

# Funcao para mandar notificacoes
def verifica_banco():
    print('lendo banco ... ')
    try:
        conn = get_db_connection()
        email_to = conn.query(Config).first().email
        data = conn.query(Boletos)
        conn.close()


        for boleto in data:
            venc = boleto.vencimento
            
            conn = get_db_connection()
            registro = conn.query(Boletos).filter_by(id=boleto.id).first()
        
            emoji = emoji_alerta(venc)
            registro.alerta = emoji[1]
            conn.commit()
            conn.close()

            dias = emoji[0]

            if dias <= 1:
                # boleto vencido
                notificacao_email(boleto, email_to, 'BOLETO VENCIDO')
                
            elif dias <= 2:
                # notificacao 3 dias para o vencimento
                notificacao_email(boleto, email_to, 'Fique atento, o boleto vence em 3 dias!')

            else:
                pass

            

    except Exception as e:
        print('Erro ao atualizar banco de dados:', str(e))

    
    

# Inicializando o aplicativo Flask
if __name__ == '__main__':

    try:   
        scheduler = BackgroundScheduler()
        scheduler.add_job(verifica_banco, 'interval', seconds=20)
        scheduler.start()
    except:
        pass

    app.run(debug=True)


