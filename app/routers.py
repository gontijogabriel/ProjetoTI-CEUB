from flask import render_template, request, redirect, flash
from datetime import datetime
from app.models import get_db_connection, Boletos, Config
from app.helpers import emoji_alerta, verifica_email
from sqlalchemy import func, asc
from app import app


@app.route('/')
def index():

    conn = get_db_connection()
    email = conn.query(Config).first()

    if email == None:
        print('No email address')

        return render_template('add_email.html')
    
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


@app.route('/cadastrar', methods=['GET', 'POST'])
def cadastrar_boleto():

    conn = get_db_connection()
    email = conn.query(Config).first()
    conn.close()

    if email == None:
        print('No email address')
        return render_template('add_email.html')

    if request.method == 'POST':
        nome = request.form['nome']
        valor = request.form['valor']
        venc = request.form['vencimento']
        alerta_h = request.form['alerta_email']
        
        vencimento = datetime.strptime(venc, '%Y-%m-%d').date()
        alerta = emoji_alerta(vencimento)[1]
        vence_em = emoji_alerta(vencimento)[0]

        conn = get_db_connection()
        novo_boleto = Boletos(nome=nome, valor=valor, vencimento=vencimento, alerta=alerta, alerta_hora=alerta_h, vence_em=vence_em)
        conn.add(novo_boleto)
        conn.commit()
        conn.close()

        flash('Boleto adicionado com sucesso!')
        return redirect('/')

    return render_template('adicionar_boleto.html')


@app.route('/pagar/<int:id>', methods=['GET', 'POST'])
def pagar_boleto(id):
    conn = get_db_connection()
    boleto = conn.query(Boletos).get(id)
    boleto.sit_pagamento = True
    conn.commit()
    conn.close()

    flash('Boleto pago!')
    return redirect('/')


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


@app.route('/excluir/<int:id>', methods=['GET', 'POST'])
def excluir_boleto(id):
    conn = get_db_connection()
    boleto = conn.query(Boletos).get(id)
    conn.delete(boleto)
    conn.commit()
    conn.close()

    flash('Boleto excluido!')
    return redirect('/')


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
        alerta = emoji_alerta(vencimento)[1]
        vence_em = emoji_alerta(vencimento)[0]

        boleto.vencimento = vencimento
        boleto.alerta = alerta
        boleto.alerta_hora = aler
        boleto.vence_em = vence_em

        conn.commit()
        conn.close()

        flash('Boleto editado!')
        return redirect('/')

    return render_template('editar.html', boleto=boleto)


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
        
        if not email or email == ' ':
            flash('O campo de e-mail não pode estar vazio!')
        else:
            if verifica_email(email):
                conn = get_db_connection()
                new_email = conn.query(Config).first()
                new_email.email = email
                conn.commit()
                conn.close()
                print('Configuração de e-mail atualizada com sucesso')

                flash('E-mail atualizado!')
                return redirect('/')

            else:
                flash('O endereço de e-mail deve ser valido!')
    

    return render_template('configuracoes.html', email=new_email)