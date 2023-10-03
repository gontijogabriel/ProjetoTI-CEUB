import smtplib
import email.message
from data import get_db_connection, Boletos, Config
from datetime import datetime


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
    msg['From'] = 'alertadeboletos@gmail.com'
    msg['To'] = email_to
    password = 'tffsyhfjokqwqvil'
    msg.add_header('Content-Type', 'text/html')
    msg.set_payload(corpo_email )

    s = smtplib.SMTP('smtp.gmail.com: 587')
    s.starttls()
    # Login Credentials for sending the mail
    s.login(msg['From'], password)
    s.sendmail(msg['From'], [msg['To']], msg.as_string().encode('utf-8'))
    
    return print('email enviado!')