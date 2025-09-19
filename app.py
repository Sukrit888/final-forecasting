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
        return df
    except FileNotFoundError:
        st.error("Error: The file 'GAIL Varanasi Sales Forecast.xlsx' was not found. Please ensure it is in the same directory.")
        st.stop()
    except Exception as e:
        st.error(f"An error occurred while reading the Excel file: {e}")
        st.stop()

# Load the data
df = load_data()

# Check if the dataframe contains at least two rows for a valid comparison
if len(df) < 2:
    st.error("Error: The dataset must contain at least two days of data for a proper comparison.")
    st.stop()

# --- Streamlit App Layout ---
st.set_page_config(layout="wide", page_title="Daily Sales Analysis", initial_sidebar_state="collapsed")

st.title("Two-Day Sales Analysis for GAIL Rameshwar Station")
st.markdown("---")

# --- Key Metrics ---
st.subheader("Key Metrics")
col1, col2 = st.columns(2)

# Sales on Day 1
day1_sales = df['Sales'].iloc[0]
day1_label = df['Day of the week'].iloc[0]
day1_nearby = df['Nearby'].iloc[0]
with col1:
    st.metric(label=f"Sales on {day1_label}", value=f"{day1_sales:,}")
    st.markdown(f"**Nearby:** {day1_nearby}")

# Sales on Day 2
day2_sales = df['Sales'].iloc[1]
day2_label = df['Day of the week'].iloc[1]
day2_nearby = df['Nearby'].iloc[1]
with col2:
    st.metric(label=f"Sales on {day2_label}", value=f"{day2_sales:,}")
    st.markdown(f"**Nearby:** {day2_nearby if pd.notna(day2_nearby) else 'N/A'}")


st.markdown("---")

# --- Visualizations ---
st.subheader("Comparative Visualizations")
col1, col2 = st.columns(2)

with col1:
    # Bar Chart: Sales Comparison by Day
    st.markdown("##### Sales per Day of the Week")
    fig_bar = px.bar(
        df,
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
        df,
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
    x=df['Day of the week'],
    y=df['Sales'],
    mode='lines+markers',
    name='Sales',
    marker_color='green'
))

# Add Temperature line plots (using a second y-axis)
fig_line.add_trace(go.Scatter(
    x=df['Day of the week'],
    y=df['Temperature (High) (Deg C)'],
    mode='lines+markers',
    name='High Temp (°C)',
    yaxis='y2',
    marker_color='red'
))
fig_line.add_trace(go.Scatter(
    x=df['Day of the week'],
    y=df['Temperatue (Low) (Deg C)'],
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

st.markdown("---")
st.markdown("This dashboard directly analyzes the two days of data provided, eliminating the need for a filter.")
