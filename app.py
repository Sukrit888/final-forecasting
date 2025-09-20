import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.preprocessing import OneHotEncoder
from sklearn.linear_model import LinearRegression
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.metrics import mean_absolute_error, mean_squared_error
import numpy as np

st.title("📈 GAIL Sales Forecasting App")

# File uploader
uploaded_file = st.file_uploader("Upload your Excel file", type=["xlsx"])
if uploaded_file:
    df = pd.read_excel(uploaded_file, sheet_name="Sheet1")
    st.subheader("Raw Data")
    st.dataframe(df)

    # Prepare features & target
    X = df[["Day of the week", "Temperature (High) (Deg C)", "Temperatue (Low) (Deg C)", "Nearby"]].copy()
    y = df["Sales"]

    # Fill missing "Nearby"
    X["Nearby"] = X["Nearby"].fillna(df["Nearby"].dropna().iloc[0])

    # Preprocessor
    categorical_features = ["Day of the week", "Nearby"]
    numeric_features = ["Temperature (High) (Deg C)", "Temperatue (Low) (Deg C)"]

    preprocessor = ColumnTransformer(
        transformers=[
            ("cat", OneHotEncoder(drop="first"), categorical_features),
            ("num", "passthrough", numeric_features)
        ]
    )

    model = Pipeline(steps=[
        ("preprocessor", preprocessor),
        ("regressor", LinearRegression())
    ])

    # Train model
    model.fit(X, y)
    y_pred = model.predict(X)

    # Metrics
    mae = mean_absolute_error(y, y_pred)
    rmse = np.sqrt(mean_squared_error(y, y_pred))

    st.subheader("Model Performance")
    st.write(f"**MAE:** {mae:.2f}")
    st.write(f"**RMSE:** {rmse:.2f}")

    # Plot
    st.subheader("Actual vs Predicted Sales")
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(df["Date"], y, marker="o", label="Actual")
    ax.plot(df["Date"], y_pred, marker="x", linestyle="--", label="Predicted")
    ax.set_xlabel("Date")
    ax.set_ylabel("Sales")
    ax.legend()
    st.pyplot(fig)

    # Future forecasting
    st.subheader("Forecast Future Sales")
    future_date = st.date_input("Select Date")
    temp_high = st.number_input("Temperature High (°C)", value=33)
    temp_low = st.number_input("Temperature Low (°C)", value=26)
    day_of_week = future_date.strftime("%A")
    nearby = df["Nearby"].dropna().iloc[0]

    if st.button("Predict Future Sales"):
        future_df = pd.DataFrame({
            "Day of the week": [day_of_week],
            "Temperature (High) (Deg C)": [temp_high],
            "Temperatue (Low) (Deg C)": [temp_low],
            "Nearby": [nearby]
        })
        prediction = model.predict(future_df)[0]
        st.success(f"📊 Predicted Sales for {future_date}: {prediction:.0f}")
