from sqlalchemy import Column, Integer, String, DECIMAL, Date, Boolean
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy import create_engine
import os
from dotenv import load_dotenv

load_dotenv()

# Modifique a URL da conexão para SQLite
engine = create_engine(os.getenv('DB'))

# Crie uma conexão com o SQLite
conn = engine.connect()

# Cria a classe base declarativa
Base = declarative_base()

# Definindo a classe do modelo
class Boletos(Base):
    __tablename__ = 'boletos'
    id = Column(Integer, primary_key=True, autoincrement=True)
    nome = Column(String(255), nullable=False)
    valor = Column(DECIMAL(10, 2), nullable=False)
    vencimento = Column(Date, nullable=False)
    alerta = Column(String(255), nullable=False)
    alerta_hora = Column(String(155), nullable=False)
    notif_3_dias = Column(Boolean, default=False)
    notif_1_dia = Column(Boolean, default=False)
    notif_venc = Column(Boolean, default=False)
    vence_em = Column(Integer, nullable=False)
    sit_pagamento = Column(Boolean, default=False)

class Config(Base):
    __tablename__ = 'email'
    email = Column(String(255), primary_key=True)

# Crie as tabelas no banco de dados SQLite
Base.metadata.create_all(engine)

def get_db_connection():
    Session = sessionmaker(bind=engine)
    session = Session()
    return session
