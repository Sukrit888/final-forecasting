import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# --- Load and Prepare Data ---
@st.cache_data
def load_data():
    """Loads the sales data from the Excel file."""
    try:
        # Load the data directly from the Excel file
        df = pd.read_excel('GAIL Varanasi Sales Forecast.xlsx')
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
st.set_page_config(layout="wide", page_title="GAIL Sales Dashboard", initial_sidebar_state="collapsed")

st.title("Sales Dashboard for GAIL Stations")
st.markdown("---")

# --- Sidebar Filters (for future scalability) ---
st.sidebar.header("Filter Data")

# Get unique stations for the selectbox
stations = df['DBS'].unique()
selected_station = st.sidebar.selectbox('Select DBS Station', stations)

# Filter the data based on the selected station
filtered_df = df[df['DBS'] == selected_station].reset_index(drop=True)

# --- Main Dashboard Content ---
if not filtered_df.empty:
    st.header(f"Insights for {selected_station}")

    # Calculate metrics
    total_sales = filtered_df['Sales'].sum()
    if len(filtered_df) > 1:
        sales_change = (filtered_df['Sales'].iloc[1] - filtered_df['Sales'].iloc[0]) / filtered_df['Sales'].iloc[0] * 100
        delta_label = f'{sales_change:.2f}%'
    else:
        sales_change = None
        delta_label = "N/A"

    # Display key metrics in columns
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(label="Total Sales", value=f"{total_sales:,}")
    with col2:
        st.metric(label="Daily Change", value=f"{filtered_df['Sales'].iloc[-1]:,}", delta=delta_label)
    with col3:
        st.metric(label="Average Temperature", value=f"{filtered_df['Temperature (High) (Deg C)'].mean():.1f} °C")

    st.markdown("---")

    # --- Row of Visualizations ---
    col1, col2 = st.columns(2)

    with col1:
        # Bar Chart: Sales per Day of the Week
        st.subheader("Sales by Day of the Week")
        fig_bar = px.bar(
            filtered_df,
            x='Day of the week',
            y='Sales',
            labels={'Day of the week': 'Day', 'Sales': 'Total Sales'},
            color='Day of the week',
            text='Sales'
        )
        fig_bar.update_traces(texttemplate='%{text:.2s}', textposition='outside')
        st.plotly_chart(fig_bar, use_container_width=True)

    with col2:
        # Pie Chart: Sales Distribution
        st.subheader("Sales Distribution")
        fig_pie = px.pie(
            filtered_df,
            values='Sales',
            names='Day of the week',
            title='Percentage of Total Sales'
        )
        fig_pie.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig_pie, use_container_width=True)

    # --- Scatter Plot for Sales vs. Temperature ---
    st.subheader("Sales vs. Temperature")
    fig_scatter = go.Figure()

    # Add high temperature data
    fig_scatter.add_trace(go.Scatter(
        x=filtered_df['Date'],
        y=filtered_df['Temperature (High) (Deg C)'],
        mode='lines+markers',
        name='High Temp (°C)',
        marker_color='red'
    ))

    # Add low temperature data
    fig_scatter.add_trace(go.Scatter(
        x=filtered_df['Date'],
        y=filtered_df['Temperatue (Low) (Deg C)'],
        mode='lines+markers',
        name='Low Temp (°C)',
        marker_color='blue'
    ))

    # Add sales data as a secondary Y-axis
    fig_scatter.add_trace(go.Scatter(
        x=filtered_df['Date'],
        y=filtered_df['Sales'],
        mode='lines+markers',
        name='Sales',
        yaxis='y2',
        marker_color='green'
    ))

    # Create two y-axes
    fig_scatter.update_layout(
        title='Sales vs. Temperature Over Time',
        yaxis=dict(title='Temperature (°C)', side='left'),
        yaxis2=dict(title='Sales', overlaying='y', side='right'),
        legend=dict(x=0.01, y=0.99, bgcolor='rgba(255, 255, 255, 0.5)')
    )

    st.plotly_chart(fig_scatter, use_container_width=True)

else:
    st.info("No data available for the selected station. Please check your data file.")
