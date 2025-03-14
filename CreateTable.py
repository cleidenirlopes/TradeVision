import pyodbc

def create_table():
    try:
        conn = pyodbc.connect(
            'DRIVER={ODBC Driver 17 for SQL Server};'
            'SERVER=localhost\\SQLExpress08;'
            'DATABASE=StockData;'
            'Trusted_Connection=yes;'
        )
        conn.autocommit = True
        cursor = conn.cursor()

        # Check if table exists, if not create it
        cursor.execute("""
            IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = 'StockData')
            BEGIN
                CREATE TABLE StockData (
                    StockID INT PRIMARY KEY IDENTITY(1,1),
                    Date DATE,
                    Ticker VARCHAR(10),
                    Company VARCHAR(255),
                    Open_Price FLOAT,
                    High_Price FLOAT,
                    Low_Price FLOAT,
                    Close_Price FLOAT,
                    Volume INT,
                    Daily_Variation FLOAT,
                    Cumulative_Variation_10 FLOAT,
                    MA_10days FLOAT,
                    MA_50days FLOAT,
                    MA_200days FLOAT,
                    Year INT,
                    Month INT,
                    Pct_Change_Daily FLOAT,
                    Pct_Change_Month FLOAT,
                    Pct_Change_Year FLOAT,
                    Trend_Label VARCHAR(50),
                    DateAdded DATETIME DEFAULT GETDATE()
                )
            END
        """)

        print("Table 'StockData' created successfully!")
        conn.close()
    except Exception as e:
        print(f"Error creating table: {e}")

create_table()

