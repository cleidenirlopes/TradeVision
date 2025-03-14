import streamlit as st
import joblib
import pyodbc
import pandas as pd
from datetime import datetime, timedelta
import plotly.graph_objects as go

# Load the model, scaler, and imputer
model = joblib.load(r"D:\Project\TradeVision\PKL\TradeVision_model.pkl")
imputer = joblib.load(r"D:\Project\TradeVision\PKL\imputer.pkl")
scaler = joblib.load(r"D:\Project\TradeVision\PKL\scaler.pkl")

# Function to fetch company info from SQL
def fetch_company_info(ticker):
    try:
        conn = pyodbc.connect(
            'DRIVER={ODBC Driver 17 for SQL Server};'
            'SERVER=localhost\\SQLExpress08;'
            'DATABASE=StockData;'
            'Trusted_Connection=yes;'
        )
        cursor = conn.cursor()
        query = """SELECT Company, Close_Price 
                   FROM StockData 
                   WHERE Ticker = ? 
                   ORDER BY Date DESC 
                   OFFSET 0 ROWS 
                   FETCH NEXT 1 ROWS ONLY;"""
        cursor.execute(query, (ticker,))
        row = cursor.fetchone()
        conn.close()

        if row:
            return row.Company, row.Close_Price
        else:
            return None, None
    except Exception as e:
        return None, None

# Function to predict stock trend based on the chosen period
def predict_stock_trend(ticker, df, model, scaler, imputer, period):
    stock_data = df[df["Ticker"] == ticker]

    if stock_data.empty:
        return "Error: No data found for this ticker."

    # Filter for the last 'n' days based on the period selected
    if period == "1 Week":
        days_to_predict = 7
    elif period == "15 Days":
        days_to_predict = 15
    elif period == "1 Month":
        days_to_predict = 30
    elif period == "6 Months":
        days_to_predict = 180

    # Get the last 'days_to_predict' rows of stock data
    stock_data = stock_data.tail(days_to_predict)

    X_stock = stock_data[['Pct_Change_Daily', 'MA_10days', 'MA_50days', 'MA_200days', 'Volume']]
    latest_data = scaler.transform(imputer.transform(X_stock))

    predicted_trend = model.predict(latest_data)[0]

    # Calculate the average percentage change and standard deviation
    avg_pct_change = stock_data['Pct_Change_Daily'].mean()
    pct_change_std = stock_data['Pct_Change_Daily'].std()

    if avg_pct_change > 0:
        trend_description = f"📈 UP by {min(abs(avg_pct_change) + pct_change_std, 5):.2f}%"
    elif avg_pct_change < 0:
        trend_description = f"📉 DOWN by {min(abs(avg_pct_change) + pct_change_std, 5):.2f}%"
    else:
        trend_description = "➖ STABLE"

    # Creating the graph
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=stock_data['Date'],
        y=stock_data['Close_Price'],
        mode='lines+markers',
        line=dict(shape='spline', smoothing=1.3, color='cyan', width=3),
        marker=dict(size=12, color='magenta', symbol='circle', opacity=0.9),
        name='Close Price'
    ))
    # Add gradient fill using multiple traces with decreasing opacity
    num_gradients = 5
    for i in range(num_gradients):
        opacity = 0.15 - (i * 0.03)  # Decreasing opacity for gradient effect
        fig.add_trace(go.Scatter(
            x=stock_data['Date'],
            y=stock_data['Close_Price'],
            fill='tonexty',
            mode='none',
            fillcolor=f'rgba(0, 255, 255, {opacity})',
            showlegend=False,
            hoverinfo='skip'
        ))

    # Add the main line trace on top
    fig.add_trace(go.Scatter(
        x=stock_data['Date'],
        y=stock_data['Close_Price'],
        mode='lines+markers',
        line=dict(
            shape='spline',
            smoothing=1.3,
            color='cyan',
            width=3
        ),
        marker=dict(
            size=12,
            color='magenta',
            symbol='circle',
            opacity=0.9
        ),
        name='Close Price'
    ))
    return trend_description, fig

def plot_graph(ticker, period):
    # Create figure and add traces as needed
    fig = go.Figure()

    # Your existing layout update
    # Update layout with enhanced styling
    fig.update_layout(
        title=dict(
            text=f"Prediction Trend for {ticker.upper()} ({period})",
            font=dict(size=26),
            x=0.5
        ),
        xaxis_title="Date",
        yaxis_title="Close Price",
        xaxis=dict(
            showgrid=False,
            tickfont=dict(size=18),
            showline=True,
            linewidth=2,
            linecolor='rgba(255, 255, 255, 0.3)'
        ),
        yaxis=dict(
            showgrid=False,
            tickfont=dict(size=18),
            showline=True,
            linewidth=2,
            linecolor='rgba(255, 255, 255, 0.3)'
        ),
        plot_bgcolor="black",
        paper_bgcolor="black",
        font=dict(color="white", size=20),
        width=800,
        height=600,
        margin=dict(l=30, r=30, t=50, b=50),
        showlegend=True,
        legend=dict(
            yanchor="top",
            y=0.99,
            xanchor="left",
            x=0.01,
            bgcolor="rgba(0,0,0,0.5)"
        )
    )

    fig.update_layout(dragmode=False)  # Disables the drag/zoom feature

    # Streamlit UI rendering
    st.plotly_chart(fig, use_container_width=False)  # Ensure custom width and height are applied

    # Return any other data you need (like trend_description)
    return "Trend Description", fig

# Streamlit UI: Stylish, Colorful & Interactive Design
st.set_page_config(page_title="TradeVision", page_icon="📈", layout="wide")

# Customizing app header and background colors using the updated color palette
st.markdown("""
    <style>
    .stApp {
        background-color: #222631;  /* Primary background color */
    }
    .stButton>button {
        background-color: #F73463;  /* Button background */
        color: #FFFFFF;  /* White text */
        font-weight: bold;
    }
    .stButton>button:hover {
        background-color: #9646EF;  /* Purple on hover */
    }
    .stTextInput>div>div>input {
        background-color: #FFFFFF;  /* White input field */
        border: 2px solid #222631;  /* Orange border */
        color: #222631;
    }
    .stTextInput>div>div>input:focus {
        border: 2px solid #43D1A7;  /* Teal border on focus */
    }
    .stMarkdown {
        color: #A0A9C0;  /* Light gray text */
    }
    .stSidebar .sidebar-content {
        background-color: #2F374C;  /* Sidebar background */
        color: #FFFFFF;  /* White text */
    }
    .stSidebar .sidebar-content a {
        color: #FFFFFF;  /* White links */
    }
    .stSidebar .sidebar-content a:hover {
        color: #A0A9C0;  /* Light grayish blue on hover */
    }
</style>
""", unsafe_allow_html=True)

st.markdown("""
    <h1 style='font-family: Poppins, sans-serif; font-size:48px; color:#FFFFFF; text-align:left;'>
        🎯 Welcome to TradeVision
    </h1>

    <br>

    <p style='font-family: Lora, serif; font-size:24px; color:#A0A9C0; text-align:left;'>
        Your go-to tool for predicting stock trends and making smarter investment decisions.
    </p>

    <p style='font-family: Lora, serif; font-size:24px; color:#A0A9C0;'>
        Whether you're an experienced trader or just starting in the stock market, 
        TradeVision provides real-time insights to help you understand market trends.  
    </p>

    <p style='font-family: Lora, serif; font-size:24px; color:#A0A9C0;'>
        Our advanced prediction model analyzes historical stock data to forecast trends 
        for the upcoming days, weeks, or months, giving you a competitive edge.
    </p>

    <br>

    <h2 style='font-family: Poppins, sans-serif; color:#FFFFFF;'>📊 What is TradeVision?</h2>

    <p style='font-family: Lora, serif; font-size:24px; color:#A0A9C0;'>
        TradeVision helps you stay ahead by predicting whether a stock’s trend will:  
    </p>

    <ul style='font-family: Lora, serif; font-size:24px; color:#A0A9C0;'>
        <li><strong>Increase</strong> 📈</li>
        <li><strong>Decrease</strong> 📉</li>
        <li><strong>Remain Stable</strong> ➖</li>
    </ul>

    <p style='font-family: Lora, serif; font-size:24px; color:#A0A9C0;'>
        The system provides clear and data-driven insights to support your investment decisions.
    </p>

    <br>

    <h2 style='font-family: Poppins, sans-serif; color:#FFFFFF;'>💡 Why was TradeVision created?</h2>

    <p style='font-family: Lora, serif; font-size:24px; color:#A0A9C0;'>
        Understanding stock trends can be challenging, especially for those without a financial background.  
    </p>

    <p style='font-family: Lora, serif; font-size:24px; color:#A0A9C0;'>
    TradeVision was designed to make stock market analysis more intuitive and accessible.
    </p>

    <p style='font-family: Lora, serif; font-size:24px; color:#A0A9C0;'>
        Whether you are evaluating new investment opportunities or tracking your portfolio,
    </p>

    <p style='font-family: Lora, serif; font-size:24px; color:#A0A9C0;'>
        this tool gives you clarity and confidence in your financial decisions.
    </p>

""", unsafe_allow_html=True)

st.markdown("""
    <div style="background-color:#2F374C; padding:5px 10px; border-radius:20px; width: 800px; text-align:center;">
        <h1 style="color:white; font-size:28px; margin:0;">Prediction Summary</h1>
    </div>

    <br>
""", unsafe_allow_html=True)

# Sidebar for user input
st.sidebar.title("🔍 Enter Stock Ticker")
ticker = st.sidebar.text_input ("Stock Ticker (e.g., MSFT, AAPL):")

# Prediction Period Selection
st.sidebar.title("🕒 Select Prediction Period")
period = st.sidebar.selectbox(
    "Choose a time period for the prediction:",
    ["1 Week", "15 Days", "1 Month", "6 Months"]
)

# Read the dataset (make sure this path is correct)
TradeVision = pd.read_csv(r"D:\Project\TradeVision\Data\Final Dataset\Final_Dataset.csv")

# Create placeholders for the dynamic values
company_placeholder = st.empty()
close_price_placeholder = st.empty()
prediction_placeholder = st.empty()

# Wrapper for inline display and alignment (using flexbox)
def create_flex_line(label, value):
    return f"""
    <div style="display: flex; align-items: center; margin-bottom: 10px;">
        <h3 style="font-size: 28px; font-weight: bold; margin-right: 10px;">{label}</h3>
        <h3 style="font-size: 28px;">{value}</h3>
    </div>
    """

if ticker:
    # Display "📡 Fetching data for ticker:" inline with the ticker value
    fetching_data_line = create_flex_line("📡 Fetching data for ticker:", ticker.upper())
    company_placeholder.write(fetching_data_line, unsafe_allow_html=True)

    # Fetch company info
    company, close_price = fetch_company_info(ticker)
    
    if company:
        # Prediction and Chart
        trend_description, fig = predict_stock_trend(ticker, TradeVision, model, scaler, imputer, period)

        # Create flexbox for the data labels and values
        company_line = create_flex_line("Company:", company)
        close_price_line = create_flex_line("Present Price:", f"${close_price:.2f}")
        
        # Display the prediction and prediction trend separately
        prediction_line = f"<h3 style='font-size: 28px;'>Prediction for the next {period}: {trend_description}</h3>"
        company_placeholder.write(company_line, unsafe_allow_html=True)
        close_price_placeholder.write(close_price_line, unsafe_allow_html=True)
        prediction_placeholder.write(prediction_line, unsafe_allow_html=True)

        # Display the interactive line chart
        st.plotly_chart(fig)
    else:
        company_placeholder.write("<h3 style='font-size: 28px;'>Error: No data found for this ticker.</h3>", unsafe_allow_html=True)
        close_price_placeholder.write("")
        prediction_placeholder.write("")
