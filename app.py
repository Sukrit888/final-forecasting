import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error
from sklearn.preprocessing import OneHotEncoder

def load_data(file_path):
    """
    Loads and preprocesses the sales data.
    """
    try:
        # Load the data from the Excel file
        df = pd.read_excel(file_path)
        
        # Clean column names
        df.columns = df.columns.str.strip().str.replace(' ', '_').str.replace('(', '').str.replace(')', '').str.lower()
        
        # Convert 'Date' to datetime objects
        df['date'] = pd.to_datetime(df['date'])
        
        # Fill missing values for categorical columns
        df['day_of_the_week'].fillna(method='ffill', inplace=True)
        df['dbs'].fillna(method='ffill', inplace=True)
        df['nearby'].fillna(method='ffill', inplace=True)
        
        return df
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return None

def preprocess_features(df):
    """
    Prepares the features for the model, including encoding categorical variables.
    """
    # Create new features from the date
    df['day_of_year'] = df['date'].dt.dayofyear
    df['month'] = df['date'].dt.month
    df['year'] = df['date'].dt.year

    # Define features and target
    features = ['day_of_the_week', 'temperature_high_deg_c', 'temperatue_low_deg_c', 'nearby']
    target = 'sales'

    # Handle the 'Nearby' feature
    # Since it's a constant value in the provided data, we'll keep it as is
    # but the model will learn to use it if more stations are added later.
    
    # Check if 'nearby' is a valid feature
    if 'nearby' in df.columns:
        # Check for multiple unique values
        if df['nearby'].nunique() > 1:
            features.append('nearby')
    
    # Handle future 'Festivals/Events' feature
    if 'festival' in df.columns:
        features.append('festival')
    
    # Separate features and target
    X = df[features]
    y = df[target]
    
    # One-hot encode the categorical features
    categorical_features = ['day_of_the_week']
    if 'nearby' in X.columns and X['nearby'].nunique() > 1:
        categorical_features.append('nearby')
    if 'festival' in X.columns:
        categorical_features.append('festival')

    encoder = OneHotEncoder(handle_unknown='ignore', sparse_output=False)
    X_encoded = encoder.fit_transform(X[categorical_features])
    
    # Get feature names after encoding
    encoded_feature_names = encoder.get_feature_names_out(categorical_features)
    
    # Combine encoded categorical features with numerical features
    numerical_features = [col for col in X.columns if col not in categorical_features]
    
    X_numerical = X[numerical_features]
    
    # Align indices to avoid issues after concatenation
    X_numerical.reset_index(drop=True, inplace=True)
    X_encoded_df = pd.DataFrame(X_encoded, columns=encoded_feature_names)
    
    X_processed = pd.concat([X_numerical, X_encoded_df], axis=1)
    
    return X_processed, y, encoder

def train_model(X_train, y_train):
    """
    Trains a Random Forest Regressor model.
    """
    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)
    return model

def evaluate_model(y_true, y_pred):
    """
    Calculates and returns MAE and RMSE.
    """
    mae = mean_absolute_error(y_true, y_pred)
    rmse = np.sqrt(mean_squared_error(y_true, y_pred))
    return mae, rmse

def plot_sales_trend(df):
    """
    Plots the daily sales trend.
    """
    fig = px.line(df, x='date', y='sales', title='Daily Sales Trend')
    st.plotly_chart(fig)

def plot_actual_vs_forecasted(df):
    """
    Plots actual vs. forecasted sales.
    """
    fig = px.line(df, x='date', y=['sales', 'forecasted_sales'], 
                  title='Actual vs. Forecasted Sales')
    fig.update_traces(patch={"line": {"dash": "dot"}}, selector={"name": "forecasted_sales"})
    st.plotly_chart(fig)

# --- Streamlit App Layout ---
st.title('GAIL Varanasi Sales Forecast')
st.markdown("""
This application loads sales data, builds a forecasting model, and visualizes the results.
""")

# Load the data from the pre-uploaded Excel file
file_path = "GAIL Varanasi Sales Forecast.xlsx"
data = load_data(file_path)

if data is not None:
    st.header('1. Data Overview')
    st.write(data.head())
    
    st.header('2. Sales Trend Analysis')
    plot_sales_trend(data)
    
    st.header('3. Forecasting Model')
    st.write("Building and training the model...")
    
    # Preprocess the data
    try:
        X, y, encoder = preprocess_features(data)
        
        # Split data into training and testing sets
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        # Train the model
        model = train_model(X_train, y_train)
        
        # Make predictions
        predictions = model.predict(X_test)
        
        # Add predictions to the test dataframe for plotting
        test_df = data.loc[y_test.index].copy()
        test_df['forecasted_sales'] = predictions
        
        st.success("Model training and forecasting complete!")
        
        st.header('4. Model Evaluation')
        mae, rmse = evaluate_model(y_test, predictions)
        st.write(f"**Mean Absolute Error (MAE):** {mae:.2f}")
        st.write(f"**Root Mean Squared Error (RMSE):** {rmse:.2f}")
        
        st.header('5. Actual vs. Forecasted Sales')
        plot_actual_vs_forecasted(test_df)
        
    except Exception as e:
        st.error(f"An error occurred during model processing: {e}")
