import pandas as pd
import pyodbc

def import_data_from_csv():
    try:
        # Read the CSV file into a DataFrame
        df = pd.read_csv(r"D:\Project\TradeVision\Data\Final Dataset\Final_Dataset.csv")

        # Drop 'Unnamed: 0' column if it exists
        if 'Unnamed: 0' in df.columns:
            df = df.drop(columns=['Unnamed: 0'])

        # Handle missing values in columns that should contain float data (e.g., MA columns)
        float_columns = [
            'Open_Price', 'High_Price', 'Low_Price', 'Close_Price', 'Volume', 
            'Daily_Variation', 'Cumulative_Variation_10', 'MA_10days', 'MA_50days', 
            'MA_200days', 'Pct_Change_Daily', 'Pct_Change_Month', 'Pct_Change_Year'
        ]

        for col in float_columns:
            # Replace NaN or missing values with 0
            df[col] = df[col].fillna(0)
            
            # Convert to float (also handle commas, if any)
            df[col] = (
                df[col]
                .astype(str)        # Convert everything to string first
                .str.replace(',', '.')  # Replace commas with dots
                .replace('', '0')   # Replace empty strings with 0
                .astype(float)      # Convert to float
            )

        # Open a connection to SQL Server
        conn = pyodbc.connect(
            'DRIVER={ODBC Driver 17 for SQL Server};'
            'SERVER=localhost\\SQLExpress08;'  
            'DATABASE=StockData;'  
            'Trusted_Connection=yes;'
        )
        cursor = conn.cursor()

        # Insert the data from the DataFrame into the SQL table
        for index, row in df.iterrows():
            cursor.execute("""
                INSERT INTO StockData (
                    Date, Ticker, Company, Open_Price, High_Price, Low_Price, Close_Price, 
                    Volume, Daily_Variation, Cumulative_Variation_10, MA_10days, MA_50days, 
                    MA_200days, Year, Month, Pct_Change_Daily, Pct_Change_Month, 
                    Pct_Change_Year, Trend_Label
                ) 
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, 
            row['Date'], row['Ticker'], row['Company'], row['Open_Price'], row['High_Price'], 
            row['Low_Price'], row['Close_Price'], row['Volume'], row['Daily_Variation'], 
            row['Cumulative_Variation_10'], row['MA_10days'], row['MA_50days'], 
            row['MA_200days'], row['Year'], row['Month'], row['Pct_Change_Daily'], 
            row['Pct_Change_Month'], row['Pct_Change_Year'], row['Trend_Label'])
        
        # Commit the transaction
        conn.commit()
        print("✅ Data imported successfully!")

        # Close connection
        conn.close()

    except Exception as e:
        print(f"❌ Error importing data: {e}")

# Call the function to import the data
import_data_from_csv()

