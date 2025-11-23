import streamlit as st
import requests
import openai
from datetime import datetime
import pandas as pd

st.set_page_config(
    page_title="WeatherAI Forecast",
    page_icon="🌤️",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        color: #1E88E5;
        text-align: center;
        margin-bottom: 2rem;
        font-weight: 700;
    }
    .weather-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 15px;
        padding: 25px;
        color: white;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        margin-bottom: 20px;
    }
    .metric-card {
        background: white;
        border-radius: 10px;
        padding: 20px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        text-align: center;
        border-left: 4px solid #1E88E5;
        margin-bottom: 15px;
    }
    .forecast-day {
        background: #f8f9fa;
        border-radius: 10px;
        padding: 15px;
        text-align: center;
        margin: 5px;
        border: 1px solid #e0e0e0;
    }
    .temp-chart {
        background: white;
        border-radius: 10px;
        padding: 20px;
        margin: 20px 0;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
    }
</style>
""", unsafe_allow_html=True)

def get_weather_data(city, weather_api_key):
    base_url = "http://api.openweathermap.org/data/2.5/weather?"
    complete_url = base_url + "appid=" + weather_api_key + "&q=" + city
    response = requests.get(complete_url)
    return response.json()

def generate_weather_description(data, openai_api_key, city):
    openai.api_key = openai_api_key
    
    try:    
        temperature = data['main']['temp'] - 273.15
        description = data['weather'][0]['description']
        humidity = data['main']['humidity']
        wind_speed = data['wind']['speed']
        
        prompt = f"""
        The current weather in {city} is {description} with a temperature of {temperature:.1f}°C, 
        {humidity}% humidity, and wind speed of {wind_speed} m/s. 
        Create a friendly, engaging weather description (2-3 sentences) that helps people plan their day.
        """
        
        response = openai.Completion.create(
            engine="gpt-3.5-turbo-instruct",
            prompt=prompt,
            max_tokens=80,
            temperature=0.7
        )
        return response.choices[0].text.strip()
    except Exception as e:  
        return f"☀️ The weather is {description} with a temperature of {temperature:.1f}°C. Perfect for going outside!"

def get_weekly_forecast(weather_api_key, lat, lon):
    base_url = "https://api.openweathermap.org/data/2.5/"
    complete_url = f"{base_url}forecast?lat={lat}&lon={lon}&appid={weather_api_key}&units=metric"
    response = requests.get(complete_url)
    return response.json()

def create_temperature_chart_simple(forecast_data):
    """Create a simple temperature chart using Streamlit's native components"""
    st.markdown("### 🌡️ 24-Hour Temperature Forecast")
    
    times = []
    temps = []
    
    for item in forecast_data['list'][:8]:
        time_str = datetime.fromtimestamp(item['dt']).strftime('%H:%M')
        times.append(time_str)
        temps.append(item['main']['temp'])
    
    chart_data = pd.DataFrame({
        'Time': times,
        'Temperature (°C)': temps
    })
    #display visualization
    st.dataframe(
        chart_data,
        column_config={
            "Time": "Time",
            "Temperature (°C)": st.column_config.ProgressColumn(
                "Temperature (°C)",
                help="Temperature trend",
                format="%.1f°C",
                min_value=min(temps) - 5,
                max_value=max(temps) + 5,
            ),
        },
        hide_index=True,
    )
    
    temp_df = pd.DataFrame({'Temperature (°C)': temps}, index=times)
    st.line_chart(temp_df, height=300)

def display_weekly_forecast(data):
    try:
        st.markdown("---")
        st.subheader("📅 5-Day Weather Forecast")
        
        daily_data = {}
        for item in data['list']:
            date = datetime.fromtimestamp(item['dt']).strftime('%Y-%m-%d')
            if date not in daily_data:
                daily_data[date] = {
                    'temps': [],
                    'descriptions': [],
                    'date': datetime.fromtimestamp(item['dt']).strftime('%a, %b %d')
                }
            daily_data[date]['temps'].append(item['main']['temp'])
            daily_data[date]['descriptions'].append(item['weather'][0]['description'])
        
        cols = st.columns(5)
        
        for idx, (date_key, day_data) in enumerate(list(daily_data.items())[:5]):
            with cols[idx]:
                avg_temp = sum(day_data['temps']) / len(day_data['temps'])
                main_description = max(set(day_data['descriptions']), key=day_data['descriptions'].count)
                
                # Weather icons
                icon = "❓"
                if "clear" in main_description: icon = "☀️"
                elif "cloud" in main_description: icon = "☁️"
                elif "rain" in main_description: icon = "🌧️"
                elif "snow" in main_description: icon = "❄️"
                elif "thunder" in main_description: icon = "⛈️"
                elif "mist" in main_description or "fog" in main_description: icon = "🌫️"
                elif "drizzle" in main_description: icon = "🌦️"
                
                st.markdown(f"""
                <div class="forecast-day">
                    <h4>{day_data['date']}</h4>
                    <div style="font-size: 2rem;">{icon}</div>
                    <h3>{avg_temp:.1f}°C</h3>
                    <p style="font-size: 0.8rem; margin: 5px 0;">{main_description.capitalize()}</p>
                </div>
                """, unsafe_allow_html=True)
                
    except Exception as e:
        st.error(f"Error displaying forecast: {str(e)}")

def main():
    with st.sidebar:
        st.markdown("<div style='text-align: center;'>", unsafe_allow_html=True)
        # Using emoji as fallback instead of image
        st.markdown("<h1 style='font-size: 4rem; margin: 0;'>🌤️</h1>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
        
        st.title("WeatherAI Forecast")
        st.markdown("---")
        
        city = st.text_input("🏙️ Enter city name", "London")
        
        weather_api_key = "87caeed2c204b469eeb8e38da821712e"
        openai_api_key = "your-openai-api-key-here"  # Replace with your actual key
        
        if st.button("🚀 Get Weather Forecast", use_container_width=True, type="primary"):
            st.session_state.get_weather = True
            st.session_state.current_city = city
        else:
            if 'get_weather' not in st.session_state:
                st.session_state.get_weather = False


    if st.session_state.get_weather:
        city = st.session_state.get('current_city', city)
        st.markdown(f'<h1 class="main-header">🌤️ Weather in {city}</h1>', unsafe_allow_html=True)
        
        with st.spinner('🔍 Fetching weather data...'):
            weather_data = get_weather_data(city, weather_api_key)

        if weather_data.get("cod") != "404":
            # Current weather card
            col1, col2 = st.columns([2, 1])
            
            with col1:
                temp = weather_data['main']['temp'] - 273.15
                description = weather_data['weather'][0]['description']
                feels_like = weather_data['main']['feels_like'] - 273.15
                
                st.markdown(f"""
                <div class="weather-card">
                    <h2>Now in {city}</h2>
                    <div style="display: flex; align-items: center; gap: 20px;">
                        <div style="font-size: 4rem; font-weight: bold;">{temp:.1f}°C</div>
                        <div>
                            <h3 style="margin: 0; font-size: 1.5rem;">{description.title()}</h3>
                            <p>Feels like {feels_like:.1f}°C</p>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                # Ai Description
                weather_description = generate_weather_description(weather_data, openai_api_key, city)
                st.info(f"💡 **AI Insights:** {weather_description}")
            
            with col2:
                # Weather metrics in cards
                metrics_data = [
                    ("💧 Humidity", f"{weather_data['main']['humidity']}%", "#4FC3F7"),
                    ("🌬️ Wind Speed", f"{weather_data['wind']['speed']} m/s", "#4DB6AC"),
                    ("📊 Pressure", f"{weather_data['main']['pressure']} hPa", "#FFB74D"),
                    ("👁️ Visibility", f"{weather_data.get('visibility', 'N/A')}", "#BA68C8")
                ]
                
                for metric, value, color in metrics_data:
                    st.markdown(f"""
                    <div class="metric-card" style="border-left-color: {color};">
                        <h4 style="margin: 0; color: {color}; font-size: 0.9rem;">{metric}</h4>
                        <h2 style="margin: 5px 0; color: #333; font-size: 1.5rem;">{value}</h2>
                    </div>
                    """, unsafe_allow_html=True)

            # Weekly forecast and charts
            lat = weather_data['coord']['lat']
            lon = weather_data['coord']['lon']
            
            forecast_data = get_weekly_forecast(weather_api_key, lat, lon)
            
            if forecast_data.get("cod") != "404":
                # Temperature chart using native Streamlit components
                create_temperature_chart_simple(forecast_data)
                
                # Weekly forecast
                display_weekly_forecast(forecast_data)
            else:
                st.error("❌ Error fetching forecast data")
        else:
            st.error("🏙️ City not found! Please check the spelling and try again.")

    else:
        # When no city is searched
        st.markdown("""
        <div style='text-align: center; padding: 100px 20px;'>
            <h1 style='font-size: 3.5rem; color: #1E88E5; margin-bottom: 20px;'>🌤️ Welcome to WeatherAI</h1>
            <p style='font-size: 1.2rem; color: #666; max-width: 600px; margin: 0 auto 40px;'>
                Get intelligent weather forecasts powered by AI. Enter a city name in the sidebar to get started!
            </p>
            <div style='font-size: 4rem; margin: 40px 0;'>
                ☀️ 🌧️ ⛅ ❄️ 🌪️
            </div>
            <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                        color: white; padding: 30px; border-radius: 15px; max-width: 500px; margin: 0 auto;'>
                <h3>🚀 Features</h3>
                <p>• Real-time weather data<br>
                   • AI-powered descriptions<br>
                   • 5-day forecast<br>
                   • Beautiful visual interface</p>
            </div>
        </div>
        """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()

