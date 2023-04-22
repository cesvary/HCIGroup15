import streamlit as st
import pandas as pd
import numpy as np
import requests
import json
from datetime import datetime
from bokeh.plotting import figure
from bokeh.models import ColumnDataSource, HoverTool
from bokeh.tile_providers import get_provider, Vendors


# Set up the API request
api_url = "https://newsdata.io/api/1/news"
api_key = "pub_20640989cdbc220e019539b45ae6f2ff6ec8f"


# Define the Streamlit app
def app():
    st.title("Global News App")

    # Get user input for location
    location = st.text_input("Enter a location (e.g. country or region):")

    # Make the API request
    params = {"apikey": api_key, "q": location}
    response = requests.get(api_url, params=params)
    news_data = json.loads(response.text)

    # Check if there are any results for the location
    if news_data["totalResults"] == 0:
        st.warning("No news found for this location.")
    else:
        # Display the news articles
        st.write(f"Displaying {len(news_data['articles'])} news articles for {location}:")
        for article in news_data["articles"]:
            st.write(article["title"])

        # Map the location of the news articles
        coordinates = []
        for article in news_data["articles"]:
            if article["location"]:
                coordinates.append(article["location"])
        if coordinates:
            center_lat = sum([coord[0] for coord in coordinates]) / len(coordinates)
            center_lon = sum([coord[1] for coord in coordinates]) / len(coordinates)
            tile_provider = get_provider(Vendors.CARTODBPOSITRON)
            map_fig = figure(tools="pan, wheel_zoom", x_range=(center_lon - 1, center_lon + 1),
                             y_range=(center_lat - 1, center_lat + 1),
                             width=800, height=600)
            map_fig.add_tile(tile_provider)
            source = ColumnDataSource(
                data={"lat": [coord[0] for coord in coordinates], "lon": [coord[1] for coord in coordinates]})
            map_fig.circle(x="lon", y="lat", source=source, size=10, color="red")
            st.bokeh_chart(map_fig, use_container_width=True)
        else:
            st.warning("No location data available for these news articles.")

        # Plot the amount of news per day
        dates = [datetime.strptime(article["publishedAt"], "%Y-%m-%dT%H:%M:%S.%fZ").strftime("%Y-%m-%d") for article in
                 news_data["articles"]]
        df = pd.DataFrame({"dates": dates})
        plot_data = df.groupby("dates").size().reset_index(name="count")
        plot_fig = figure(x_axis_type="datetime", width=800, height=400)
        plot_fig.line(x=plot_data["dates"], y=plot_data["count"])
        plot_fig.add_tools(HoverTool(tooltips=[("Date", "@x{%F}"), ("Count", "@y")]))
