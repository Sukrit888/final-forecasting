import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import date

def load_data(file_path):
    """
    Loads and preprocesses the sales data from an Excel file.
    """
    try:
        # Load the data from the Excel file
        df = pd.read_excel(file_path)
        
        # Clean column names for easier access
        df.columns = df.columns.str.strip().str.replace(' ', '_').str.replace('(', '').str.replace(')', '').str.lower()
        
        # Convert 'Date' to datetime objects for proper handling
        df['date'] = pd.to_datetime(df['date'])
        
        # Fill missing values for categorical columns by propagating the last valid observation
        df['day_of_the_week'].fillna(method='ffill', inplace=True)
        df['dbs'].fillna(method='ffill', inplace=True)
        df['nearby'].fillna(method='ffill', inplace=True)
        
        return df
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return None

def plot_sales_trend(df):
    """
    Plots the daily sales trend over time using a line chart.
    """
    fig = px.line(df, x='date', y='sales', title='Daily Sales Trend')
    st.plotly_chart(fig)

# --- Streamlit App Layout ---
st.title('GAIL Varanasi Daily Sales Analysis')
st.markdown("""
This application allows you to select a specific date and view a detailed analysis of sales for that day, based on weather and other factors.
""")

# Load the data from the pre-uploaded Excel file
file_path = "GAIL Varanasi Sales Forecast.xlsx"
data = load_data(file_path)

if data is not None:
    st.header('1. Data Overview')
    st.write("Here is a quick look at the raw data:")
    st.write(data.head())
    
    st.header('2. Sales Trend')
    st.write("A line chart showing the sales trend over the available dates.")
    plot_sales_trend(data)
    
    st.header('3. Daily Sales Analysis')
    st.write("Select a date to see the sales and contributing factors for that specific day.")

    # Create a date picker for the user to select a date
    min_date = data['date'].min().date()
    max_date = data['date'].max().date()
    selected_date = st.date_input("Select a date", min_value=min_date, max_value=max_date, value=min_date)

    # Filter the DataFrame for the selected date
    selected_row = data[data['date'].dt.date == selected_date]

    if not selected_row.empty:
        # Extract the relevant information from the filtered row
        sales = selected_row['sales'].iloc[0]
        day_of_week = selected_row['day_of_the_week'].iloc[0]
        temp_high = selected_row['temperature_high_deg_c'].iloc[0]
        temp_low = selected_row['temperatue_low_deg_c'].iloc[0]
        nearby = selected_row['nearby'].iloc[0]
        
        # Display the analysis for the selected day
        st.write(f"### Analysis for {selected_date.strftime('%B %d, %Y')}")
        st.write(f"**Sales:** {sales}")
        st.write(f"**Day of the week:** {day_of_week}")
        st.write(f"**Weather:** High of {temp_high}°C, Low of {temp_low}°C")
        st.write(f"**Nearby Locations:** {nearby}")

        # Provide a simple conclusion based on the sales figure
        median_sales = data['sales'].median()
        st.write(f"The median daily sales across the dataset is: {median_sales:.2f}")

        if sales > median_sales:
            st.success(f"**Conclusion:** Sales on this day were above the dataset's median.")
        else:
            st.info(f"**Conclusion:** Sales on this day were below or around the dataset's median.")
            
    else:
        st.warning("No data available for the selected date.")
