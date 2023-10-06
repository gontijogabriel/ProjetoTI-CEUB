import smtplib
import email.message
from app.models import Boletos, Config, engine
from datetime import datetime
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError
from dotenv import load_dotenv
import re
import os

load_dotenv()

Session = sessionmaker(bind=engine)

def emoji_alerta(venc):
    hoje = datetime.now().date()

    dias = venc - hoje
    dias = dias.days

    if dias <= 0:
        return [dias,'❌']

    elif dias >= 1 and dias <= 3:
        return [dias,'🔴']
    
    elif dias >= 4 and dias <= 6:
        return [dias,'🟡']
    
    else:
        return [dias,'🟢']


def notificacao_email(boleto, email_to, msg):
    corpo_email = f"""
    <h1>Alerta de Boletos</h1>
    <p>Referente ao boleto: <strong>{boleto.nome}</stong></p>
    <p><strong>{msg}</strong></p>
    <p>Vencimento: {boleto.vencimento}</p>
    <p>Valor: {boleto.valor}</p>
    <p>ass: Alerta de Boletos</p>
    """

    msg = email.message.Message()
    msg['Subject'] = "ALERTA"
    msg['From'] = os.getenv("EMAIL_HOST")
    msg['To'] = email_to
    password = os.getenv("PASSWORD_DB")
    msg.add_header('Content-Type', 'text/html')
    msg.set_payload(corpo_email )

    s = smtplib.SMTP('smtp.gmail.com: 587')
    s.starttls()
    # Login Credentials for sending the mail
    s.login(msg['From'], password)
    s.sendmail(msg['From'], [msg['To']], msg.as_string().encode('utf-8'))
    
    return print('email enviado!')


def verifica_banco():
    print('lendo banco ... ')
    try:
        with Session() as session:
            email_to = session.query(Config).first().email
            boletos_pendentes = session.query(Boletos).filter_by(sit_pagamento=False).all()

            for boleto in boletos_pendentes:
                ntf_3 = boleto.notif_3_dias
                ntf_1 = boleto.notif_1_dia
                ntf_v = boleto.notif_venc

                dias = emoji_alerta(boleto.vencimento)[0]

                # Atualize os boletos dentro do escopo da sessão
                boleto.vence_em = dias
                boleto.alerta = emoji_alerta(boleto.vencimento)[1]
                session.commit()

                if dias <= 0 and ntf_v == False:
                    # Atualize o boleto dentro do escopo da sessão
                    boleto.notif_venc = True
                    session.commit()

                    now = datetime.now().time()
                    alert_time = (boleto.alerta_hora)[:2]

                    if str(now.hour) == alert_time[:2]:
                        notificacao_email(boleto, email_to, 'BOLETO VENCIDO')

                elif dias == 1 and not ntf_1:
                    # Atualize o boleto dentro do escopo da sessão
                    boleto.notif_1_dia = True
                    session.commit()

                    now = datetime.now().time()
                    alert_time = (boleto.alerta_hora)[:2]

                    if str(now.hour) == alert_time[:2]:
                        notificacao_email(boleto, email_to, 'O boleto vence amanha')

                elif 1 < dias <= 3 and not ntf_3:
                    # Atualize o boleto dentro do escopo da sessão
                    boleto.notif_3_dias = True
                    session.commit()

                    now = datetime.now().time()
                    alert_time = (boleto.alerta_hora)[:2]
                    if str(now.hour) == alert_time[:2]:
                        notificacao_email(boleto, email_to, 'O boleto vence em 3 dias!')

    except SQLAlchemyError as erro:
        print(f"Ocorreu um erro no SQLAlchemy: {erro}")
    except Exception as erro:
        print(f"Ocorreu um erro: {erro}")


def verifica_email(email):
    # Padrão de expressão regular para validar endereços de e-mail
    padrao = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    
    # Tenta fazer a correspondência do padrão no email fornecido
    if re.match(padrao, email):
        return True
    else:
        return False