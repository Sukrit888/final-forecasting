import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import date

# --- Load and Prepare Data ---
@st.cache_data
def load_data():
    """
    Loads the sales data from the Excel file and performs data cleaning.
    """
    try:
        df = pd.read_excel('GAIL Varanasi Sales Forecast.xlsx', sheet_name='Sheet1')
        df['Date'] = pd.to_datetime(df['Date']).dt.date
        df['DBS'] = df['DBS'].ffill()
        return df
    except FileNotFoundError:
        st.error("Error: The file 'GAIL Varanasi Sales Forecast.xlsx' was not found.")
        st.stop()
    except Exception as e:
        st.error(f"An error occurred while reading the Excel file: {e}")
        st.stop()

# Load the data
df = load_data()

# --- Streamlit App Layout ---
st.set_page_config(layout="wide", page_title="Daily Sales Analysis & Forecasting", initial_sidebar_state="collapsed")

# --- Sidebar for User Input ---
st.sidebar.header("Filter Options")
stations = sorted(df['DBS'].dropna().unique().tolist())
if not stations:
    st.sidebar.error("No stations found in the 'DBS' column.")
    st.stop()

selected_station = st.sidebar.selectbox("Select a Station", stations)

station_df = df[df['DBS'] == selected_station].copy()
if station_df.empty:
    st.sidebar.warning(f"No data available for {selected_station}.")
    st.stop()

dates = sorted(station_df['Date'].unique().tolist())
if not dates:
    st.sidebar.warning(f"No dates found for {selected_station}.")
    st.stop()

selected_date = st.sidebar.selectbox(
    "Select a Date",
    options=dates,
    index=len(dates) - 1 if dates else 0
)

filtered_df = station_df[station_df['Date'] == selected_date].copy()

if filtered_df.empty:
    st.warning(f"No data found for the selected date: {selected_date}.")
    st.stop()

# --- Main Dashboard ---
st.title(f"Daily Sales Analysis for {selected_station} Station")
st.markdown("---")

# Display common information
nearby_info = filtered_df['Nearby'].iloc[0] if pd.notna(filtered_df['Nearby'].iloc[0]) else 'N/A'
st.markdown(f"**Nearby Locations:** {nearby_info}")
st.markdown("---")

# --- Key Metrics ---
st.subheader("Sales and Weather Details")

day_data = filtered_df.iloc[0]

st.markdown(f"### {day_data['Day of the week']} ({day_data['Date']})")
st.metric(label="Total Sales", value=f"₹{day_data['Sales']:,}")
st.markdown(
    f"**Temperature:** High {day_data['Temperature (High) (Deg C)']}°C, "
    f"Low {day_data['Temperatue (Low) (Deg C)']}°C"
)

st.markdown("---")

# --- Sales Forecasting Section ---
st.subheader("Sales Forecasting")
st.info(
    "**Note:** To create a meaningful sales forecast, we need a time-series dataset with sales "
    "data for multiple days. With only one day selected, it's impossible to predict future "
    "trends. This section would be used to show a forecast based on a larger dataset."
)
