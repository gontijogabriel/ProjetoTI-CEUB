from sqlalchemy import Column, Integer, String, Numeric
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
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
        nome = Column(String(255))  # Especifique o comprimento máximo desejado
        valor = Column(Numeric(10, 2))  # Usando tipo Numeric para valores monetários
        vencimento = Column(String(10))  # Especifique o comprimento máximo desejado, por exemplo, 10 caracteres
        alerta = Column(String(255))  # Especifique o comprimento máximo desejado, por exemplo, 255 caracteres
        situacao_pagamento = Column(String(255))



    class Config(Base):
        __tablename__ = 'email'
        email = Column(String(255), primary_key=True)  # Definindo a coluna como chave primária

    # Crie as tabelas no banco de dados
    engine = create_engine('mysql+mysqlconnector://root:root@localhost:3306/alugacar')
    Base.metadata.create_all(engine)

except mysql.connector.Error as e:
    print(f"Erro ao conectar ao banco de dados: {e}")

def get_db_connection():
    Session = sessionmaker(bind=engine)  # Use o engine criado anteriormente
    session = Session()
    return session
