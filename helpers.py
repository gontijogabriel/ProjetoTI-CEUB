import smtplib
import email.message
from data import get_db_connection, Boletos, Config


senha = 'tffsyhfjokqwqvil'

def notificacao_email(boleto):

    # pega email do banco
    conn = get_db_connection()
    email_to = conn.query(Config).first().email
    conn.close()

    corpo_email = """
    <h1>Alerta de Boletos</h1>
    <p>O boleto {{ boleto.nome }} vai vencer em breve!!!</p>
    <p>Vencimento: {{ boleto.vencimento }}</p>
    <p>Valor: {{ boleto.valor }}</p>
    """

    msg = email.message.Message()
    msg['Subject'] = "ALERTA"
    msg['From'] = 'alertadeboletos@gmail.com'
    msg['To'] = email_to
    password = senha
    msg.add_header('Content-Type', 'text/html')
    msg.set_payload(corpo_email )

    s = smtplib.SMTP('smtp.gmail.com: 587')
    s.starttls()
    # Login Credentials for sending the mail
    s.login(msg['From'], password)
    s.sendmail(msg['From'], [msg['To']], msg.as_string().encode('utf-8'))
    print('Email enviado')