# Import necessary libraries
import streamlit as st
import requests
import openai
from datetime import datetime

# Function to get weather data from OpenWeatherMap API
def get_weather_data(city, weather_api_key):
    try:
        base_url = "http://api.openweathermap.org/data/2.5/weather?"
        complete_url = f"{base_url}appid={weather_api_key}&q={city}"
        response = requests.get(complete_url)
        response.raise_for_status()  # Raises exception for 4XX/5XX errors
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"API request failed: {str(e)}")
        return None

def generate_weather_description(data, openai_api_key):
    if not data or 'main' not in data or 'weather' not in data:
        return "Could not generate description: Invalid weather data"
    
    try:
        openai.api_key = openai_api_key
        temperature = data['main']['temp'] - 273.15
        description = data['weather'][0]['description']
        prompt = f"The current weather is {description} with a temperature of {temperature:.1f}°C. Explain this in simple, friendly terms."
        
        response = openai.Completion.create(
            engine="gpt-3.5-turbo-instruct",
            prompt=prompt,
            max_tokens=60,
            temperature=0.7
        )
        return response.choices[0].text.strip()
    except Exception as e:
        return f"Could not generate description: {str(e)}"

def get_weekly_forecast(weather_api_key, lat, lon):
    try:
        base_url = "https://api.openweathermap.org/data/2.5/forecast"
        complete_url = f"{base_url}?lat={lat}&lon={lon}&appid={weather_api_key}"
        response = requests.get(complete_url)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Forecast API request failed: {str(e)}")
        return None
    
def display_weekly_forecast(data):
    if not data or 'list' not in data:
        st.error("No forecast data available")
        return
        
    try:
        st.write("---")
        st.subheader("Weekly Weather Forecast")
        displayed_dates = set()
        
        cols = st.columns(4)
        headers = ["Day", "Description", "Min Temp", "Max Temp"]
        for col, header in zip(cols, headers):
            col.metric("", header)
        
        for day in data['list']:
            date = datetime.fromtimestamp(day['dt']).strftime('%a, %b %d')
            
            if date not in displayed_dates:
                displayed_dates.add(date)
                try:
                    min_temp = day['main']['temp_min'] - 273.15
                    max_temp = day['main']['temp_max'] - 273.15
                    description = day['weather'][0]['description']
                    
                    cols = st.columns(4)
                    cols[0].write(date)
                    cols[1].write(description.capitalize())
                    cols[2].write(f"{min_temp:.1f}°C")
                    cols[3].write(f"{max_temp:.1f}°C")
                except KeyError:
                    continue
                    
    except Exception as e:
        st.error(f"Error displaying forecast: {str(e)}")

def main():
    # Sidebar configuration
    st.sidebar.image("logo.jpg", width=120, caption="Weather App")
    st.sidebar.title("Weather Forecasting with AI")
    city = st.sidebar.text_input("Enter city name", "New York")
    
    # API keys - should use st.secrets in production
    weather_api_key = st.secrets.get("WEATHER_API_KEY", "your_default_key")
    openai_api_key = st.secrets.get("OPENAI_API_KEY", "your_default_key")
    
    if st.sidebar.button("Get Weather", type="primary"):
        st.title(f"Weather Updates for {city}")
        
        with st.spinner('Fetching weather data...'):
            weather_data = get_weather_data(city, weather_api_key)
            
            if not weather_data:
                return
                
            if weather_data.get("cod") != 200:
                error_msg = weather_data.get('message', 'Unknown error occurred')
                st.error(f"Weather API Error: {error_msg}")
                return
                
            # Current Weather Display
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Temperature", 
                         f"{weather_data['main']['temp'] - 273.15:.1f}°C",
                         help="Current temperature")
                st.metric("Humidity", 
                         f"{weather_data['main']['humidity']}%",
                         help="Relative humidity")
            with col2:
                st.metric("Pressure", 
                         f"{weather_data['main']['pressure']} hPa",
                         help="Atmospheric pressure")
                st.metric("Wind Speed", 
                         f"{weather_data['wind']['speed']} m/s",
                         help="Wind speed")
            
            # Weather Description
            with st.expander("Weather Description"):
                description = generate_weather_description(weather_data, openai_api_key)
                st.write(description)
            
            # Weekly Forecast
            lat = weather_data['coord']['lat']
            lon = weather_data['coord']['lon']
            
            with st.spinner('Fetching weekly forecast...'):
                forecast_data = get_weekly_forecast(weather_api_key, lat, lon)
                if forecast_data:
                    display_weekly_forecast(forecast_data)

if __name__ == "__main__":
    main()
