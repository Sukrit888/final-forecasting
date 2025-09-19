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

# --- Interactive Filters ---
st.sidebar.header("Filter Data")

# Get unique stations for the selectbox
stations = df['DBS'].unique()
selected_station = st.sidebar.selectbox('Select DBS Station', stations)

# Filter the data based on the selected station
filtered_df = df[df['DBS'] == selected_station].reset_index(drop=True)

# --- Main Dashboard Content ---
if not filtered_df.empty:
    st.header(f"Insights for {selected_station}")

    # Display key metrics for both days
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(label=f"Sales on {filtered_df['Day of the week'].iloc[0]}", value=f"{filtered_df['Sales'].iloc[0]:,}")
    with col2:
        st.metric(label=f"Sales on {filtered_df['Day of the week'].iloc[1]}", value=f"{filtered_df['Sales'].iloc[1]:,}")
    with col3:
        sales_change = filtered_df['Sales'].iloc[1] - filtered_df['Sales'].iloc[0]
        # Delta color based on sales change
        delta_color = "inverse" if sales_change < 0 else "normal"
        st.metric(label="Sales Change", value=f"Change: {sales_change:+,}", delta_color=delta_color)

    st.markdown("---")

    # --- Row of Visualizations ---
    col1, col2 = st.columns(2)

    with col1:
        # Bar Chart: Sales per Day of the Week
        st.subheader("Sales Comparison")
        fig_bar = px.bar(
            filtered_df,
            x='Day of the week',
            y='Sales',
            title='Sales per Day of the Week',
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

    # --- Combined Sales and Temperature Plot ---
    st.subheader("Sales vs. Temperature Over Time")
    fig_line = go.Figure()

    # Add Sales line plot
    fig_line.add_trace(go.Scatter(
        x=filtered_df['Day of the week'],
        y=filtered_df['Sales'],
        mode='lines+markers',
        name='Sales',
        marker_color='green'
    ))

    # Add Temperature line plots
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

else:
    st.info("No data available for the selected station. Please check your data file.")
