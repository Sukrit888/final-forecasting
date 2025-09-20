import streamlit as st
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error
import numpy as np
import openpyxl

# --- 1. Load and clean the dataset ---
@st.cache_data
def load_data(file_path):
    """
    Loads and preprocesses the sales data from an Excel file.
    """
    try:
        # Load the data from the Excel file
        df = pd.read_excel(file_path)
        
        # Clean column names for easier access (e.g., lowercase, replace spaces with underscores)
        df.columns = df.columns.str.strip().str.replace(' ', '_').str.replace('(', '').str.replace(')', '').str.lower()
        
        # Convert 'date' to datetime objects for proper handling
        df['date'] = pd.to_datetime(df['date'])
        
        # Fill missing values for categorical columns by propagating the last valid observation
        df['day_of_the_week'].fillna(method='ffill', inplace=True)
        df['dbs'].fillna(method='ffill', inplace=True)
        df['nearby'].fillna(method='ffill', inplace=True)
        
        return df
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return None

# --- Main Streamlit App ---
def main():
    st.title('GAIL Varanasi Sales Forecasting')
    st.markdown("---")
    
    # Path to the uploaded file
    file_path = "GAIL Varanasi Sales Forecast.xlsx"
    data = load_data(file_path)

    if data is not None:
        
        # --- 2. Analyze the trend of Sales for all the available dates ---
        st.header('1. Daily Sales Trend Analysis')
        st.write("A table showing the sales trend over the available dates.")
        
        st.dataframe(data[['date', 'sales']].set_index('date').rename(columns={'sales': 'Actual Sales'}), use_container_width=True)
        st.markdown("---")

        # --- 3. Build a forecasting model ---
        st.header('2. Sales Forecasting Model')
        st.write("A Linear Regression model is used to forecast daily sales based on several factors.")

        # Prepare features for the model
        features = data[['day_of_the_week', 'temperature_high_deg_c', 'temperatue_low_deg_c', 'dbs', 'nearby']].copy()
        target = data['sales'].copy()

        # Add a placeholder column for future events/festivals
        features['festivals_events'] = 0

        # One-hot encode categorical features to make them usable for the model
        features_encoded = pd.get_dummies(features, columns=['day_of_the_week', 'dbs', 'nearby'], drop_first=True)

        # Split data for potential training (although here we will forecast the whole dataset for comparison)
        X = features_encoded
        y = target
        
        # Train the Linear Regression model
        model = LinearRegression()
        model.fit(X, y)

        # --- 4. Forecast the sales and display error metrics ---
        st.header('3. Forecasting Results & Error Metrics')
        
        # Make predictions on the entire dataset
        predictions = model.predict(X)
        
        # Calculate error metrics
        mae = mean_absolute_error(y, predictions)
        rmse = np.sqrt(mean_squared_error(y, predictions))
        
        st.write("### Model Performance")
        st.info(f"**Mean Absolute Error (MAE):** {mae:.2f}")
        st.info(f"**Root Mean Squared Error (RMSE):** {rmse:.2f}")
        st.write("""
        * **MAE:** The average difference between the actual and predicted sales. A lower value indicates a more accurate model.
        * **RMSE:** The standard deviation of the prediction errors. It gives more weight to large errors.
        """)
        st.markdown("---")
        
        # --- 5. Display a table comparing actual vs. forecasted Sales ---
        st.header('4. Actual vs. Forecasted Sales Table')
        
        # Create a DataFrame for comparison table
        comparison_df = pd.DataFrame({
            'Date': data['date'].dt.strftime('%Y-%m-%d'),
            'Actual Sales': y,
            'Forecasted Sales': predictions.round(2)
        })
        
        st.dataframe(comparison_df.set_index('Date'), use_container_width=True)

if __name__ == "__main__":
    main()
