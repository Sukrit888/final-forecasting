import streamlit as st
import pandas as pd
import io
import altair as alt
import requests
import json
import time

# --- Data as strings (read from user-provided files) ---
data_july_2023 = """Week,Saturday,Sunday,Monday,Tuesday,Wednesday,Thursday,Friday
Week 1 (1–7),2761,2503,2236,3340,2824,3150,3035
Week 2 (8–14),3219,3057,1269,2479,3220,3089,2656
Week 3 (15–21),3138,3018,3034,2845,3089,2945,3268
Week 4 (22–28),2795,3087,2752,3227,3140,2711,3295
Week 5 (29-31),2327,3021,2877,0,0,0,0
Total Sales,14240,14686,12168,11891,12273,11895,12254
Average Sales,2848,2937.2,2433.6,2972.75,3068.25,2973.75,3063.5
Reasoning,"Mixed weather, but strong festival weekends","High footfall, especially 9th and 23rd July.","Shravan Mondays (10, 17, 24, 31 July) boosted temple footfall.","Stable weather, high weekday footfall.","","",""
"""

data_august_2023 = """Week,Tuesday,Wednesday,Thursday,Friday,Saturday,Sunday,Monday
Week 1 (1-7),3350,3139,3140,2731,2885,2601,2847
Week 2 (8- 14),2777,3106,3243,2929,3218,3290,3217
Week 3 (15-21),3273,3391,3246,3389,3138,3232,2665
Week 4 (22-28),3345,2833,3279,3170,2942,2782,3130
Week 5 (29-31),3320,3455,2770,0,0,0,0
Total Sales,16065,15924,15678,12219,12183,11905,11859
Average Sales,3213,3184.8,3135.6,2443.8,2436.6,2381,2371.8
Reasoning,"Hanuman Day boosted temple footfall","High weekday engagement due to commute to college/work","Stable weather, consistent traffic","Dip in sales due to heavy rain","Weekend beginning, reducing commute to college or work","Surge in sales due to a resort nearby","Slight dip in sales due to people going back to their places of work"
"""

data_september_2023 = """Week,Friday,Saturday,Sunday,Monday,Tuesday,Wednesday,Thursday
Week 1 (1-7),2721,3985,1662,2186,3026,2897,2523
Week 2 (8-14),2793,2520,2697,2427,2725,1956,2590
Week 3 (15-21),2920,2993,2365,2370,2899,3400,3055
Week 4 (22-28),2968,2138,2664,2843,3084,2895,2836
Week 5 (29-30),3043,2419,0,0,0,0,0
Total Sales,14445,14055,9388,9826,11734,11148,11004
Average Sales,2889,2811,1877.6,1965.2,2346.8,2229.6,2200.8
Reasoning,"Friday prayers increased Idgah footfall","Weekend beginning, reducing commute to work or college","Dip in sales due to people moving to and from the city during weekend","Surge in sales due to week commencement","High weekday engagement","Pleasant weather","Nearby HPCL filling station diverted minimal sales"
"""

data_october_2023 = """Week,Sunday,Monday,Tuesday,Wednesday,Thursday,Friday,Saturday
Week 1 (1-7),3053,2788,2458,1936,2901,2603,2975
Week 2 (8-14),3121,2931,3171,2504,2752,3086,1946
Week 3 (15-21),2812,3159,2762,3114,2392,2950,2963
Week 4 (22-28),2795,2908,2548,1577,2255,2767,2654
Week 5 (29-31),2653,2911,3092,0,0,0,0
Total Sales,14434,14697,14031,9131,10300,11406,10538
Average Sales,2886.8,2939.4,2806.2,1826.2,2060,2281.2,2107.6
Reasoning,"Nearby resort boosted footfall","Week commencement, increasing commute to school and work","Bharat Milap on 24October increased footfall","Power cuts caused dip in sales","Nearby HPCL filling station boosted sales","High weekday engagement","Weekend commencement, nearby resort boosted sales"
"""

data_november_2023 = """Week,Wednesday,Thursday,Friday,Saturday,Sunday,Monday,Tuesday
Week 1 (1-7),2546,1950,2953,2601,2412,2185,2864
Week 2 (8-14),2894,3011,2793,2697,1782,1825,2655
Week 3 (15-21),3183,3430,3079,3189,2591,3120,3345
Week 4 (22-28),3893,3448,3033,3260,3555,2300,3488
Week 5 (29-30),3269,3160,0,0,0,0,0
Total Sales,15785,14999,11858,11747,10340,9430,12352
Average Sales,3157,2999.8,2371.6,2349.4,2068,1886,2470.4
Reasoning,"Festive mood boosted sales, especially on 1st Nov as Panch Koshi Parikrama commenced","Panch Koshi Parikrama on 2nd Nov and weekday commute to work or college","Slight dip in sales due to people moving from the city due to festivities","Commencement of weekend","Diwali on 12th Nov increased footfall.","Sales boosted by a nearby resort on Sunday.",""
"""

data_december_2023 = """Week,Friday,Saturday,Sunday,Monday,Tuesday,Wednesday,Thursday
Week 1 (1-7),3030,3065,3176,2585,2956,3373,3111
Week 2 (8-14),2970,3496,3030,3046,3377,3411,3151
Week 3 (15-21),3588,3284,2233,3041,3204,3721,2994
Week 4 (22-28),3182,3206,3112,3367,3262,3321,2908
Week 5 (29-31),3425,3157,1739,0,0,0,0
Total Sales,16195,16208,13290,12039,12799,13826,12164
Average Sales,3239,3241.6,2658,2407.8,2559.8,2765.2,2432.8
Reasoning,"Friday prayers increased Idgah footfall","Weekend commute to resort boosted sales","New Year's eve on 31st Dec boosted sales in adverse weather conditions","Low Visibility contributed to dip in sales","Increased temple footfall due to Hanuman Day","High weekday engagement","Adverse weather negatively impacted sales throughout the week"
"""

# Mapping of month to data string
MONTH_DATA = {
    "July 2023": data_july_2023,
    "August 2023": data_august_2023,
    "September 2023": data_september_2023,
    "October 2023": data_october_2023,
    "November 2023": data_november_2023,
    "December 2023": data_december_2023,
}

# Define the positive and negative impact keywords and their corresponding multipliers
IMPACT_FACTORS = {
    "positive": {
        "boosted": 1.10,
        "surge": 1.10,
        "high footfall": 1.10,
        "festival": 1.10,
        "increased": 1.05,
        "high weekday engagement": 1.05,
        "stable weather": 1.05,
        "pleasant weather": 1.05,
        "new year's eve": 1.15
    },
    "negative": {
        "dip": 0.90,
        "low": 0.95,
        "heavy rain": 0.90,
        "power cuts": 0.90,
        "adverse weather": 0.90,
        "diverted": 0.95,
        "reducing commute": 0.95
    }
}

API_KEY = ""
API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-preview-05-20:generateContent"

def generate_note_with_api(input_reasoning):
    """Generates a predictive note using a large language model."""
    if not input_reasoning:
        return "No significant change expected."

    prompt = (
        "Based on the following factors from previous year sales data: "
        f"'{input_reasoning}'. "
        "Generate a concise, predictive note for a sales forecast. "
        "The note should sound like a business analyst's comment and be forward-looking."
        "The tone should be professional and straightforward. Do not mention 2023."
    )
    
    headers = {
        'Content-Type': 'application/json'
    }

    payload = {
        "contents": [
            {
                "parts": [
                    {
                        "text": prompt
                    }
                ]
            }
        ],
        "systemInstruction": {
            "parts": [{ "text": "You are a helpful assistant that generates sales forecast notes based on given historical data."}]
        }
    }

    try:
        response = requests.post(f"{API_URL}?key={API_KEY}", headers=headers, data=json.dumps(payload))
        response.raise_for_status()
        response_json = response.json()
        generated_text = response_json['candidates'][0]['content']['parts'][0]['text']
        return generated_text.replace('\n', ' ')
    except requests.exceptions.RequestException as e:
        st.error(f"API call failed: {e}")
        return "Note generation failed due to an API error."
    except KeyError:
        return "Note generation failed: Unexpected API response format."
    except Exception as e:
        return f"An unexpected error occurred: {e}"

def load_and_preprocess_data(month_name):
    """Loads data from the embedded string and preprocesses it."""
    try:
        data = MONTH_DATA.get(month_name)
        df = pd.read_csv(io.StringIO(data), skipinitialspace=True)
        # Assuming the 'Average Sales' row is the second to last one
        avg_sales_row = df[df['Week'] == 'Average Sales']
        
        reasoning_row = df[df['Week'] == 'Reasoning']
        
        # Create a dictionary of average sales and reasoning for each day
        day_sales = {}
        day_reasoning = {}
        
        day_columns = [col for col in df.columns if col not in ['Week', 'Total Sales', 'Average Sales', 'Reasoning']]
        
        for i, day in enumerate(day_columns):
            day_sales[day] = float(avg_sales_row.iloc[0][day])
            day_reasoning[day] = reasoning_row.iloc[0][day] if not pd.isna(reasoning_row.iloc[0][day]) else ""

        return day_sales, day_reasoning
        
    except Exception as e:
        st.error(f"Error loading data for {month_name}: {e}")
        return None, None

def forecast_sales(day_sales, day_reasoning):
    """Applies a simple rule-based forecast."""
    forecasted_sales = day_sales.copy()
    notes = {}

    for day, reason in day_reasoning.items():
        final_multiplier = 1.0
        applied_factors = []

        # Check for positive factors
        for keyword, multiplier in IMPACT_FACTORS["positive"].items():
            if keyword in reason.lower():
                final_multiplier *= multiplier
                applied_factors.append(f"Positive Factor: '{keyword}' (+{int((multiplier - 1) * 100)}%)")

        # Check for negative factors
        for keyword, multiplier in IMPACT_FACTORS["negative"].items():
            if keyword in reason.lower():
                final_multiplier *= multiplier
                applied_factors.append(f"Negative Factor: '{keyword}' ({int((multiplier - 1) * 100)}%)")

        forecasted_sales[day] = round(day_sales[day] * final_multiplier, 2)
        
        # Use the API to generate a new note
        note_text = generate_note_with_api(", ".join(applied_factors))
        notes[day] = note_text

    return forecasted_sales, notes

def forecast_multiple_years(day_sales, day_reasoning, num_years):
    """Forecasts sales for multiple years."""
    all_forecasts = {}
    current_sales = day_sales.copy()
    
    for year in range(1, num_years + 1):
        forecasted_sales, notes = forecast_sales(current_sales, day_reasoning)
        year_label = f"Year {2023 + year}"
        all_forecasts[year_label] = pd.DataFrame([forecasted_sales, notes], index=['Forecasted Average Sales (Units)', 'Notes']).T
        current_sales = forecasted_sales
    return all_forecasts


# --- Streamlit App UI ---
st.set_page_config(page_title="GAIL Varanasi Sales Forecast", layout="wide")

st.title("GAIL Varanasi Sales Forecasting Dashboard")
st.write("This app forecasts average daily sales for future years based on the reasoning provided in the 2023 sales data.")

# Sidebar for month selection and year range
st.sidebar.header("Forecast Settings")
selected_month = st.sidebar.selectbox("Choose a month to view historical and forecasted data:", list(MONTH_DATA.keys()))
num_years_to_forecast = st.sidebar.selectbox("Number of years to forecast:", range(1, 6), index=0)

st.header(f"Sales Data & Forecast for {selected_month}")

# Load and display 2023 data
day_sales_2023, day_reasoning_2023 = load_and_preprocess_data(selected_month)

if day_sales_2023:
    st.subheader(f"2023 Average Sales & Reasoning ({selected_month})")
    df_2023 = pd.DataFrame([day_sales_2023, day_reasoning_2023], index=['Average Sales (Units)', 'Reasoning']).T
    st.dataframe(df_2023, use_container_width=True)

    # Multi-year forecast
    all_forecasts = forecast_multiple_years(day_sales_2023, day_reasoning_2023, num_years_to_forecast)

    # Display tables for each forecasted year
    st.header("Multi-Year Forecast")
    
    for year, df_forecast in all_forecasts.items():
        st.subheader(f"Forecast for {year}")
        st.dataframe(df_forecast, use_container_width=True)

    # Prepare data for the line chart
    line_chart_data = {
        'Day': list(day_sales_2023.keys()),
        "2023 Actual": list(day_sales_2023.values())
    }
    
    for year, df_forecast in all_forecasts.items():
        line_chart_data[year] = df_forecast['Forecasted Average Sales (Units)'].values

    df_line_chart = pd.DataFrame(line_chart_data)
    df_line_chart = df_line_chart.set_index('Day')

    # Melt the dataframe to long format for Altair
    df_melted = df_line_chart.reset_index().melt('Day', var_name='Year', value_name='Sales')

    st.subheader("Sales Trend Over the Years")

    # Create the Altair chart
    chart = alt.Chart(df_melted).mark_line(point=True).encode(
        # Set the x-axis to be the 'Day' with an explicit order
        x=alt.X('Day', sort=list(df_line_chart.index)),
        # Set the y-axis to be 'Sales' with a title
        y=alt.Y('Sales', title='Average Daily Sales (Units)'),
        # Color the lines based on the 'Year'
        color=alt.Color('Year'),
        # Add tooltips for interactivity
        tooltip=['Day', 'Year', alt.Tooltip('Sales', format=',.2f')]
    ).properties(
        title=f"Sales Trend Over the Years ({selected_month})",
        width=800,  # Set a fixed width for better visibility
        height=500  # Set a fixed height
    ).interactive()

    st.altair_chart(chart, use_container_width=True)
    
else:
    st.error("Could not load data for the selected month. Please check the data format.")
