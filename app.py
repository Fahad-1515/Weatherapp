# Import necessary libraries
import streamlit as st
import requests
import openai
from datetime import datetime

# Function to get weather data from OpenWeatherMap API
def get_weather_data(city, weather_api_key):
    base_url = "http://api.openweathermap.org/data/2.5/weather?"
    complete_url = base_url + "appid=" + weather_api_key + "&q=" + city
    response = requests.get(complete_url)
    return response.json()

def generate_weather_description(data, openai_api_key):
    openai.api_key = openai_api_key
    
    try:    
        # Convert temperature from Kelvin to Celsius
        temperature = data['main']['temp'] - 273.15
        description = data['weather'][0]['description']
        prompt = f"The current weather in your city is {description} with a temperature of {temperature:.1f}°C. Explain this in simple words."
        
        response = openai.Completion.create(
            engine="gpt-3.5-turbo-instruct",
            prompt=prompt,
            max_tokens=60
        )
        return response.choices[0].text.strip()  # Fixed index from [8] to [0]
    except Exception as e:  
        return f"Could not generate description: {str(e)}"

def get_weekly_forecast(weather_api_key, lat, lon):
    base_url = "https://api.openweathermap.org/data/2.5/"
    complete_url = f"{base_url}forecast?lat={lat}&lon={lon}&appid={weather_api_key}"
    response = requests.get(complete_url)
    return response.json()
    
def display_weekly_forecast(data):
    try:
        st.write("---")
        st.write("### Weekly Weather Forecast")
        displayed_dates = set()
        
        c1, c2, c3, c4 = st.columns(4)
        
        # Column headers
        with c1:
            st.metric("", "Day")
        with c2:
            st.metric("", "Description")
        with c3:
            st.metric("", "Min Temp")
        with c4:
            st.metric("", "Max Temp")
        
        for day in data['list']:
            date = datetime.fromtimestamp(day['dt']).strftime('%a, %b %d')
            
            if date not in displayed_dates:
                displayed_dates.add(date)
                min_temp = day['main']['temp_min'] - 273.15
                max_temp = day['main']['temp_max'] - 273.15
                description = day['weather'][0]['description']
                
                with c1:
                    st.write(f"{date}")
                with c2:
                    st.write(f"{description.capitalize()}")
                with c3:
                    st.write(f"{min_temp:.1f}°C")
                with c4:
                    st.write(f"{max_temp:.1f}°C")
                    
    except Exception as e:
        st.error(f"Error displaying forecast: {str(e)}")

def main():
    # Sidebar configuration
    st.sidebar.image("logo.jpg", width=120)  # Fixed st.sidebarimage to st.sidebar.image
    st.sidebar.title("Weather Forecasting with LLM")
    city = st.sidebar.text_input("Enter city name", "New York")  # Fixed "NewYork" to "New York"
    
    # API keys (Note: These should be environment variables in production)
    weather_api_key = "your_openweather_api_key"
    openai_api_key = "your_openai_api_key"
    
    submit = st.sidebar.button("Get Weather")

    if submit:
        st.title(f"Weather Updates for {city}:")  # Fixed string formatting
        with st.spinner('Fetching weather data...'):
            weather_data = get_weather_data(city, weather_api_key)

        if weather_data.get("cod") != "404":  # Compare with string "404" not integer
            col1, col2 = st.columns(2)  # Fixed variable name from coll to col1
            with col1:
                st.metric("Temperature", f"{weather_data['main']['temp'] - 273.15:.2f}°C")  # Fixed temperature symbol
                st.metric("Humidity", f"{weather_data['main']['humidity']}%")
            with col2:
                st.metric("Pressure", f"{weather_data['main']['pressure']} hPa")  # Fixed unit to hPa
                st.metric("Wind Speed", f"{weather_data['wind']['speed']} m/s")

            lat = weather_data['coord']['lat']
            lon = weather_data['coord']['lon']
            
            weather_description = generate_weather_description(weather_data, openai_api_key)
            st.write(weather_description)
            
            forecast_data = get_weekly_forecast(weather_api_key, lat, lon)  # Fixed to call correct function
            
            if forecast_data.get("cod") != "404":
                display_weekly_forecast(forecast_data)
            else:
                st.error("Error in fetching weekly forecast data")
        else:
            st.error("City not found or an error occurred!")

if __name__ == "__main__":
    main()
