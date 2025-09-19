import streamlit as st
import pandas as pd
import plotly.express as px

# --- Load and Prepare Data ---
@st.cache_data
def load_data():
    """Loads the sales data from the Excel file."""
    try:
        # Load the data directly from the Excel file
        df = pd.read_excel('GAIL Varanasi Sales Forecast.xlsx')
        # Filter for the specific station and the two days of data
        df_rameshwar = df[(df['DBS'] == 'Rameshwar') | (df['Date'] == '2023-07-02')]
        return df_rameshwar
    except FileNotFoundError:
        st.error("Error: The file 'GAIL Varanasi Sales Forecast.xlsx' was not found.")
        st.stop()
    except Exception as e:
        st.error(f"An error occurred while reading the Excel file: {e}")
        st.stop()

# Load the data
df = load_data()

# --- Streamlit App Layout ---
st.set_page_config(layout="wide", page_title="DBS Rameshwar Sales Analysis")

st.title("Sales Analysis for DBS Rameshwar Station")
st.markdown("---")

# --- Detailed Report Section ---
st.header("Detailed Sales Report")

# Check for data availability
if not df.empty:
    sales_saturday = df[df['Day of the week'] == 'Saturday']['Sales'].iloc[0]
    sales_sunday = df[df['Day of the week'] == 'Sunday']['Sales'].iloc[0]
    nearby_saturday = df[df['Day of the week'] == 'Saturday']['Nearby'].iloc[0]
    temperature_high = df['Temperature (High) (Deg C)'].iloc[0]
    temperature_low = df['Temperatue (Low) (Deg C)'].iloc[0]

    st.markdown(
        f"""
        This report analyzes the sales performance of the DBS Rameshwar station over a two-day period,
        specifically Saturday, July 1st, and Sunday, July 2nd, 2023.

        ### Key Findings:
        * **Total Sales:** The total sales for Saturday were **{sales_saturday}** and for Sunday were **{sales_sunday}**.
            There was a slight decrease in sales on Sunday, with a drop of **{sales_saturday - sales_sunday}** compared to Saturday.

        * **Day of the Week:** The most significant factor influencing this change is likely the **day of the week**.
            Sales on Saturdays often benefit from a combination of weekend traffic and pre-holiday travel.
            In contrast, Sundays might see slightly reduced sales as travel patterns shift towards returning home or preparing for the new week.

        * **Temperature:** The temperature for both days was consistent, with a high of **{temperature_high}°C** and a low of **{temperature_low}°C**.
            Since the temperature remained unchanged, it is not a contributing factor to the observed sales difference between these two days.

        * **Nearby Infrastructure:** The report indicates that the station is located near the **{nearby_saturday}** on Saturday.
            This proximity to various points of interest (a resort, college, and other businesses) likely contributes to a consistent flow of customers. The lack of nearby information for Sunday's sales could suggest a lack of traffic or a different customer base on that day, though this is speculative.

        **Conclusion:** The minor drop in sales from Saturday to Sunday is most likely attributed to the natural change in customer behavior over the weekend, rather than external factors like temperature. Further analysis with more days of data would be necessary to identify any long-term sales trends.
        """
    )

    st.markdown("---")

    # --- Visualization Section ---
    st.header("Sales Visualization")

    # Create a bar chart using Plotly
    fig = px.bar(
        df,
        x='Day of the week',
        y='Sales',
        title='Sales Comparison: Saturday vs. Sunday',
        labels={'Day of the week': 'Day of the Week', 'Sales': 'Total Sales'},
        color='Day of the week',
        text='Sales'
    )

    # Customize the chart
    fig.update_traces(texttemplate='%{text}', textposition='outside')
    fig.update_layout(uniformtext_minsize=8, uniformtext_mode='hide')

    # Display the chart in Streamlit
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")

    # --- Raw Data Section ---
    st.header("Raw Data")
    st.dataframe(df)

else:
    st.info("No data available to display. Please ensure the Excel file is in the same directory.")
