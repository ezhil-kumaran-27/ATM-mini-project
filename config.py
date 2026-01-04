import psycopg2

def get_db_connection():
    connection = psycopg2.connect(
        host="localhost",
        database="atm_db",
        user="postgres",
        password="postgres@123",
    )
    return connection