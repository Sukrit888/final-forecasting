import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# --- Load and Prepare Data ---
@st.cache_data
def load_data():
    """
    Loads the sales data from the Excel file.
    Assumes a single Excel sheet with the specified column names.
    """
    try:
        # Load the data directly from the Excel file
        df = pd.read_excel('GAIL Varanasi Sales Forecast.xlsx', sheet_name='Sheet1')
        df['Date'] = pd.to_datetime(df['Date']).dt.date
        
        # Data Cleaning: Fill empty 'DBS' values with the previous non-empty value
        # This is a robust way to handle the station name being missing on subsequent rows
        df['DBS'] = df['DBS'].ffill()
        
        return df
    except FileNotFoundError:
        st.error("Error: The file 'GAIL Varanasi Sales Forecast.xlsx' was not found. Please ensure it is in the same directory.")
        st.stop()
    except Exception as e:
        st.error(f"An error occurred while reading the Excel file: {e}")
        st.stop()

# Load the data
df = load_data()

# --- Streamlit App Layout ---
st.set_page_config(layout="wide", page_title="Daily Sales Analysis", initial_sidebar_state="collapsed")

# --- Sidebar for User Input ---
st.sidebar.header("Filter Options")

# Get unique station names
stations = sorted(df['DBS'].dropna().unique().tolist())
if not stations:
    st.sidebar.error("No stations found in the 'DBS' column.")
    st.stop()

# Station selection
selected_station = st.sidebar.selectbox("Select a Station", stations)

# Filter data by selected station
station_df = df[df['DBS'] == selected_station].copy()
if station_df.empty:
    st.sidebar.warning(f"No data available for {selected_station}.")
    st.stop()

# Get unique dates for the selected station
dates = sorted(station_df['Date'].unique().tolist())
if len(dates) < 2:
    st.sidebar.warning(f"Not enough data for a two-day comparison for {selected_station}.")
    st.stop()

# Date selection
selected_dates = st.sidebar.multiselect(
    "Select Two Dates for Comparison",
    options=dates,
    default=dates[-2:] if len(dates) >= 2 else dates
)

# Filter data by selected dates
if len(selected_dates) != 2:
    st.warning("Please select exactly two dates to compare.")
    st.stop()

filtered_df = station_df[station_df['Date'].isin(selected_dates)].sort_values('Date').copy()

# --- Main Dashboard ---
st.title(f"Two-Day Sales Analysis for {selected_station} Station")
st.markdown("---")

# Display common information
nearby_info = filtered_df['Nearby'].iloc[0] if pd.notna(filtered_df['Nearby'].iloc[0]) else 'N/A'
st.markdown(f"**Nearby Locations:** {nearby_info}")
st.markdown("---")

# --- Key Metrics ---
st.subheader("Key Metrics")
col1, col2 = st.columns(2)

# Sales on Day 1
day1_sales = filtered_df['Sales'].iloc[0]
day1_label = filtered_df['Day of the week'].iloc[0]
with col1:
    st.metric(label=f"Sales on {day1_label}", value=f"{day1_sales:,}")

# Sales on Day 2
day2_sales = filtered_df['Sales'].iloc[1]
day2_label = filtered_df['Day of the week'].iloc[1]
with col2:
    st.metric(label=f"Sales on {day2_label}", value=f"{day2_sales:,}")

st.markdown("---")

# --- Visualizations ---
st.subheader("Comparative Visualizations")
col1, col2 = st.columns(2)

with col1:
    # Bar Chart: Sales Comparison by Day
    st.markdown("##### Sales per Day of the Week")
    fig_bar = px.bar(
        filtered_df,
        x='Day of the week',
        y='Sales',
        title='Sales Comparison',
        labels={'Day of the week': 'Day', 'Sales': 'Total Sales'},
        color='Day of the week',
        text='Sales'
    )
    fig_bar.update_traces(textposition='outside')
    st.plotly_chart(fig_bar, use_container_width=True)

with col2:
    # Pie Chart: Sales Distribution
    st.markdown("##### Sales Distribution")
    fig_pie = px.pie(
        filtered_df,
        values='Sales',
        names='Day of the week',
        title='Percentage of Total Sales'
    )
    fig_pie.update_traces(textposition='inside', textinfo='percent+label')
    st.plotly_chart(fig_pie, use_container_width=True)

# Combined Sales and Temperature Plot
st.markdown("##### Sales vs. Temperature Over Time")
fig_line = go.Figure()

# Add Sales line plot
fig_line.add_trace(go.Scatter(
    x=filtered_df['Day of the week'],
    y=filtered_df['Sales'],
    mode='lines+markers',
    name='Sales',
    marker_color='green'
))

# Add Temperature line plots (using a second y-axis)
fig_line.add_trace(go.Scatter(
    x=filtered_df['Day of the week'],
    y=filtered_df['Temperature (High) (Deg C)'],
    mode='lines+markers',
    name='High Temp (°C)',
    yaxis='y2',
    marker_color='red'
))
fig_line.add_trace(go.Scatter(
    x=filtered_df['Day of the week'],
    y=filtered_df['Temperatue (Low) (Deg C)'],
    mode='lines+markers',
    name='Low Temp (°C)',
    yaxis='y2',
    marker_color='blue'
))

# Create two y-axes for different scales
fig_line.update_layout(
    title='Sales & Temperature',
    xaxis_title='Day of the Week',
    yaxis=dict(title='Sales', side='left'),
    yaxis2=dict(title='Temperature (°C)', overlaying='y', side='right', showgrid=False),
    legend=dict(x=0.01, y=0.99)
)

st.plotly_chart(fig_line, use_container_width=True)
