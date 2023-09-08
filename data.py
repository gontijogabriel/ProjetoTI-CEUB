from sqlalchemy import create_engine, Column, Integer, String, Numeric
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

# Cria a conexão com o banco de dados
engine = create_engine('sqlite:///boletos.db', echo=True)

# Cria a classe base declarativa
Base = declarative_base()

# Definindo a classe do modelo
class Boletos(Base):
    __tablename__ = 'boletos'
    id = Column(Integer, primary_key=True)
    nome = Column(String)
    valor = Column(Numeric(10, 2))  # Usando tipo Numeric para valores monetários
    vencimento = Column(String)
    alerta = Column(String)
    situacao_pagamento = Column(String)

class Config(Base):
    __tablename__ = 'email'
    email = Column(String, primary_key=True)  # Definindo a coluna como chave primária

# Cria as tabelas no banco de dados
Base.metadata.create_all(engine)

def get_db_connection():
    Session = sessionmaker(bind=engine)
    conn = Session()
    return conn