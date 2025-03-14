import pyodbc

def create_database():
    try:
        conn = pyodbc.connect(
            'DRIVER={ODBC Driver 17 for SQL Server};'
            'SERVER=localhost\\SQLExpress08;'
            'DATABASE=master;'
            'Trusted_Connection=yes;'
        )
        conn.autocommit = True  # Explicitly set autocommit to True
        cursor = conn.cursor()
        cursor.execute("CREATE DATABASE StockData")
        print("Database 'StockData' created successfully!")
        conn.close()
    except Exception as e:
        print(f"Error creating database: {e}")

create_database()
