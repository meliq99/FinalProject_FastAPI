from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from decouple import config


# SQLALCHEMY_DATABASE_ULR = config('DATABASE_URL') 
db_user = config('POSTGRES_USER')
db_password = config('POSTGRES_PASSWORD')
db_database = config('POSTGRES_DATABASE')
db_host = config('POSTGRES_HOST')
db_port = config('POSTGRES_PORT')

SQLALCHEMY_DATABASE_URL = f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_database}"
engine = create_engine(SQLALCHEMY_DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# It's important to only call create_all after you've defined your models
Base.metadata.create_all(bind=engine)

Base.metadata.bind = engine

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
