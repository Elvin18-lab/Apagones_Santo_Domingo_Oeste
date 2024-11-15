from sqlalchemy import create_engine

def get_connection():
    return create_engine('postgresql://postgres:EgRjEpfPLsdgCTCQRAgyfSaIdBatsHQI@postgres.railway.internal:5432/railway').connect()
