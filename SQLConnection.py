import pyodbc

def SQLConnection():
    try:
        conn = pyodbc.connect(
            'DRIVER={ODBC Driver 17 for SQL Server};'
            'SERVER=localhost\\SQLExpress08;'  # Use your instance name
            'DATABASE=master;'
            'Trusted_Connection=yes;'
        )
        print("✅ Connection Successful!")
        conn.close()
    except Exception as e:
        print(f"❌ Connection Failed: {e}")

SQLConnection()
# Output: ✅ Connection Successful!



