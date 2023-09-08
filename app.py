# Importando as bibliotecas necessárias
from flask import Flask, render_template, request, redirect
import sqlite3
import datetime
from data import get_db_connection, Boletos, Config


app = Flask(__name__)


@app.route('/')
def index():
    conn = get_db_connection()
    boletos = conn.query(Boletos).all()
    conn.close()

    boletos_view = []
    soma = []
    for b in boletos:
        if b.situacao_pagamento == 'ausente':
            boletos_view.append(b)
            soma.append(b.valor)

    return render_template('index.html', boletos=boletos_view, valorTotal=sum(soma))


# Rota 2 - cadastrar um novo boleto
@app.route('/cadastrar', methods=['GET', 'POST'])
def cadastrar_boleto():
    if request.method == 'POST':
        nome = request.form['nome']
        vencimento = request.form['vencimento']
        alerta = request.form['alerta']
        valor = request.form['valor']

        conn = get_db_connection()
        novo_boleto = Boletos(nome=nome, vencimento=vencimento, alerta=alerta, valor=valor,
                            situacao_pagamento='ausente')
        conn.add(novo_boleto)
        conn.commit()
        conn.close()

        return redirect('/')

    return render_template('adicionar_boleto.html')


# Rota 3 - pagar boleto
@app.route('/pagar/<int:id>', methods=['GET', 'POST'])
def pagar_boleto(id):
    data = datetime.datetime.now()
    # Formato desejado, você pode personalizá-lo
    formato = "%d/%m/%Y - %H:%M:%S"
    data_pagamento = data.strftime(formato)

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
        if b.situacao_pagamento != 'ausente':
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
        vencimento = request.form['vencimento']
        alerta = request.form['alerta']
        valor = request.form['valor']
        
        conn = get_db_connection()
        boleto = conn.query(Boletos).filter(Boletos.id == id).first()
        boleto.nome = nome
        boleto.vencimento = vencimento
        boleto.alerta = alerta
        boleto.valor = valor
        conn.commit()
        conn.close()

        return redirect('/')

    return render_template('editar.html', boleto=boleto)

# Rota para configurar notificações
@app.route('/configurar', methods=['GET', 'POST'])
def configurar_notificacoes():

    conn = get_db_connection()
    email = conn.query(Config).first()
    conn.close

    if email:

        conn = get_db_connection()
        email = conn.query(Config).first()
        placeholder_mail = email.email
        conn.commit()
        conn.close()

        if request.method == 'POST':
            conn = get_db_connection()
            email_form = request.form['email']

            mail = conn.query(Config).filter(Config.email).first()
            mail.email = email_form

            conn.commit()
            conn.close()

            return render_template('/')
    


    else:
        print('nao ha email no banco')
        email = input('Email para notificacao: ')
        new_e = Config(email=email)

        conn = get_db_connection()
        email = conn.add(new_e)
        placeholder_mail = new_e.email
        conn.commit()
        conn.close()

        return render_template('/configuracoes.html', email=placeholder_mail)



# Configurando a rota padrão para limpar o banco de dados
@app.route('/limpar', methods=['POST'])
def limpar_banco_dados():
    conn = get_db_connection()
    conn.execute('DELETE FROM boletos')
    conn.commit()
    conn.close()
    
    return redirect('/')


# Inicializando o aplicativo Flask
if __name__ == '__main__':
    app.run(debug=True)