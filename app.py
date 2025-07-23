#import necessary libraries
import streamlit as st
import requests
import openai
from datetime import datetime

#Function to get seather data from OpenleatherMap API
def get_weather_data(city, weather_api_key):
    base_url = "http://api.openweathermap.org/data/2.5/weather?"
    complete_url = base_url + "appid="+ weather_api_key + "&q=" + city
    response = requests.get(complete_url)
    return response.json()

def generate_weather_description(data, openai_api_key):
    openai.api_key = openai_api_key
    
    try:    
        #Convert temperature from Kelvin to Celsius
        temperature = data['main']['temp'] - 273.15  #Convert Kelvin to Celsius
        description= data['weather'][0]['description']
        prompt="The current weather in your city is {description} with a temperature of {temperature:.1f}*C.Explain this in simple words."
        
        response = openai.Completion.create(
            engine="gpt-3.5-turbo-instruct",
            prompt=prompt,
            max_tokens=60
        )
        return response.choices[8].text.strip()
    except Exception as e:  
        return str(e)

    def get_weekly_forecast(weather_api_key, lat, lon):
        base_url = "https://api.openweathermap.org/data/2.5/"
        complete_url = f"{base_url}forecast?lat={lat}&lon={lon}&appid={weather_api_key}"
        response = requests.get(complete_url)
        return response.json()
    
    #function to display weakly weather forecast
    

def display_weekly_forecast(data):
    try:
        st.write("===============================================================================================================================")
        st.write("### Weekly Weather Forecast")
        displayed_dates = set()  # To keep track of dates for which forecast has been displayed
        
        # Create columns
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
        
        # Process each forecast entry
        for day in data['list']:
            date = datetime.fromtimestamp(day['dt']).strftime('%a, %b %d')
            
            # Check if the date has already been displayed
            if date not in displayed_dates:
                displayed_dates.add(date)
                
                # Extract weather data
                min_temp = day['main']['temp_min'] - 273.15  # Convert Kelvin to Celsius
                max_temp = day['main']['temp_max'] - 273.15
                description = day['weather'][0]['description']
                
                # Display data in columns
                with c1:
                    st.write(f"{date}")
                with c2:
                    st.write(f"{description.capitalize()}")
                with c3:
                    st.write(f"{min_temp:.1f}°C")
                with c4:
                    st.write(f"{max_temp:.1f}°C")
                    
    except Exception as e:
        st.error(f"Error in displaying weekly forecast" + str(e))

#main function to run streamlit app
def main():
    #Sidebar configuration
    st.sidebarimage("logo.jpg",width=120)
    st.sidebar.title("Weather Forecasting with LLM")
    city = st.sidebar.text_input("Enter city name", "NewYork")
    
    #API keys
    weather_api_key = "7a18c45635ad6fdc20cb9d8340fbadee" #Replace with your OpenlleatherMap API key
    openai_api_key = "sk-yxlarFitqgdoKnflitswT3BLbkFJuy SPOvEqXoqavqlax2mm" # Replace with your OpenAI API key
    
    #Button to fetch and display weather data
    submit=st.sidebar.button("Get Weather")

    if submit:
        st.title("Weather Updates for " + city + "is:")
        with st.spinner('Fetching seather data...'):
            weather_data = get_weather_data(city, weather_api_key)
            print(weather_data)

        #Check if the city is found and display weather data
        if weather_data.get("cod") != 404:
            coll, col2=st.columns(2)
        with coll:
            st.metric("Temperature ",f"{weather_data['main']['temp'] - 273.15:.2f} ৹C")
            st.metric("Humidity", f"{weather_data['main']['humidity']}%")
        with col2:
            st.metric("Pressure", f"{weather_data['main']['pressure']} hpa")
            st.metric("Wind Speed", f"{weather_data['wind']['speed']} m/s")

        lat = weather_data['coord']['lat']
        lon = weather_data['coord']['lon']
        
        #Generate and display a friendly weather description
        weather_description = generate_weather_description(weather_data, openai_api_key)
        st.write(weather_description)
        
        #call function to get weekly forecast
        forecast_data = get_weather_data(city, weather_api_key, lat, lon)
        
        print(forecast_data)
        
        if forecast_data.get("cod")!= "404":
            display_weekly_forecast(forecast_data)
            
        else:
            st.error("Error in fetching weekly forecast data")
            
    else:
        #Display an error message if the city is not found
        st.error("City not found or an error occurred!")



if __name__ == "__main__":
    main()