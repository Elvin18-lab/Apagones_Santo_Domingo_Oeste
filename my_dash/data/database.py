from sqlalchemy import create_engine

def get_connection():
    return create_engine('postgresql://postgres:elvin123@localhost:5432/apagones_db').connect()
