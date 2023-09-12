from sqlalchemy import Column, Integer, String, DECIMAL, Date, Boolean
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy import create_engine  # Importe a função create_engine
import mysql.connector

try:
    # Estabelece a conexão com o banco de dados
    conn = mysql.connector.connect(
        host="localhost",
        port=3306,
        user="root",
        password="root",
        database="alugacar"
    )

    if conn.is_connected():
        print("Conexão ao banco de dados estabelecida com sucesso!")

    # Cria a classe base declarativa
    Base = declarative_base()

    # Definindo a classe do modelo
    class Boletos(Base):
        __tablename__ = 'boletos'
        id = Column(Integer, primary_key=True, autoincrement=True)
        nome = Column(String(255), nullable=False)
        valor = Column(DECIMAL(10,2), nullable=False)
        vencimento = Column(Date, nullable=False)
        notificacao_3 = Column(Boolean, default=False)
        notificacao_venc = Column(Boolean, default=False)
        situacao_pagamento = Column(Date)

    class Config(Base):
        __tablename__ = 'email'
        email = Column(String(255), primary_key=True) 

    # Crie as tabelas no banco de dados
    engine = create_engine('mysql+mysqlconnector://root:root@localhost:3306/alugacar')
    Base.metadata.create_all(engine)

except mysql.connector.Error as e:
    print(f"Erro ao conectar ao banco de dados: {e}")

def get_db_connection():
    Session = sessionmaker(bind=engine)  # Use o engine criado anteriormente
    session = Session()
    return session
