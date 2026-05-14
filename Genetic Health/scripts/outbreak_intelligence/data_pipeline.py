import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def generate_synthetic_bangalore_data(days=365*3):
    """
    Generates realistic synthetic epidemiological and environmental data for Bangalore.
    Simulates seasonality, monsoons, and historical Dengue outbreak patterns.
    """
    np.random.seed(42)
    dates = pd.date_range(end=datetime.today(), periods=days)
    
    # Simulate Base Temperature and Rainfall for Bangalore
    # Bangalore gets mostly rain from June to October
    days_of_year = dates.dayofyear
    
    # Rainfall: Higher probability and intensity between days 150 (End May) and 300 (End Oct)
    rain_prob = np.where((days_of_year > 150) & (days_of_year < 300), 0.6, 0.1)
    rainfall_mm = np.random.binomial(1, rain_prob) * np.random.gamma(shape=2, scale=10, size=days)
    
    # Temperature: Higher in Mar-May (days 60-150), lower in Dec-Jan
    temp_c = 25 + 5 * np.sin(2 * np.pi * (days_of_year - 100) / 365) + np.random.normal(0, 1.5, days)
    
    # Humidity: Correlated with rainfall
    humidity = 50 + 30 * np.clip(rainfall_mm / 50, 0, 1) + np.random.normal(0, 5, days)
    humidity = np.clip(humidity, 30, 95)
    
    df = pd.DataFrame({
        'date': dates,
        'temperature_c': temp_c,
        'rainfall_mm': rainfall_mm,
        'humidity_percent': humidity
    })
    
    return df

def engineer_features(df):
    """
    Creates lag features and rolling averages necessary for outbreak prediction.
    """
    # Lag features for environment (it takes time for mosquitoes to breed after rain)
    df['rain_lag_7'] = df['rainfall_mm'].shift(7)
    df['rain_lag_14'] = df['rainfall_mm'].shift(14)
    df['temp_lag_7'] = df['temperature_c'].shift(7)
    df['humidity_lag_7'] = df['humidity_percent'].shift(7)
    
    # Rolling averages for environment
    df['rain_rolling_14'] = df['rainfall_mm'].rolling(window=14).mean()
    df['temp_rolling_7'] = df['temperature_c'].rolling(window=7).mean()
    
    # Simulate Dengue Cases based on environmental features
    # More rain + optimal temp (25-30C) -> more mosquitoes -> more cases 2-3 weeks later
    base_cases = 5
    
    # Optimal temp multiplier
    temp_multiplier = np.where((df['temp_lag_7'] > 25) & (df['temp_lag_7'] < 30), 1.5, 1.0)
    
    # Rain multiplier
    rain_multiplier = 1 + (df['rain_rolling_14'].fillna(0) / 20)
    
    expected_cases = base_cases * temp_multiplier * rain_multiplier
    
    # Add noise and make it an integer count
    df['dengue_cases'] = np.random.poisson(expected_cases.fillna(base_cases))
    
    # Epidemiological lag features
    df['cases_lag_7'] = df['dengue_cases'].shift(7)
    df['cases_rolling_14'] = df['dengue_cases'].rolling(window=14).mean()
    
    # Drop rows with NaN due to shifting
    df = df.dropna().reset_index(drop=True)
    
    return df

def get_processed_data():
    """Main pipeline function."""
    raw_df = generate_synthetic_bangalore_data()
    processed_df = engineer_features(raw_df)
    return processed_df

if __name__ == "__main__":
    df = get_processed_data()
    print(df.tail())
    df.to_csv('bangalore_dengue_synthetic.csv', index=False)
    print("Data saved to bangalore_dengue_synthetic.csv")
