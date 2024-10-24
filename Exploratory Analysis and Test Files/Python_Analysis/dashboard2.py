import streamlit as st
import pandas as pd
import folium
import json
import geopandas as gpd
from streamlit_folium import folium_static
from branca.colormap import linear

# Load population and mortality data
with open('Population_Mortality_2013_2023.json') as f:
    data = json.load(f)

df = pd.json_normalize(data)

# Load country locations and GeoJSON data
with open('countries.json') as f:
    country_locations = json.load(f)['country_locations']

geo_df = gpd.read_file('countries.geojson')

# Function to create a map
def create_map(data, title):
    # Initialize a Folium map
    m = folium.Map(location=[20, 0], zoom_start=2)

    # Create a linear colormap for color scaling (Greens)
    colormap = linear.Greens.scale(data['value'].min(), data['value'].max())

    # Add a choropleth layer
    folium.Choropleth(
        geo_data=geo_df,
        name='choropleth',
        data=data,
        columns=['Country Name', 'value'],  # Adjust based on the data structure
        key_on='feature.properties.ADMIN',
        fill_color='Greens',  # Use a colormap that is always available
        fill_opacity=0.6,
        line_opacity=0.2,
        legend_name=title,
        line_color='black',
        highlight=True,
    ).add_to(m)

    # Add the colormap to the map
    colormap.caption = title
    colormap.add_to(m)

    folium.LayerControl().add_to(m)
    return m

# Sidebar options for user input
st.sidebar.header("Filter Options")
selected_series = st.sidebar.selectbox("Select Series Name", df['Series Name'].unique())
selected_year = st.sidebar.selectbox("Select Year", df.columns[3:])  # Assuming years start from the 4th column

# Filter the data based on selections
filtered_data = df[df['Series Name'] == selected_series]
filtered_data['value'] = filtered_data[selected_year]

# Create maps
st.title("Population and Mortality Data Visualization")

# Map 1: Population by Country
st.header(f"{selected_series} in {selected_year}")
population_map = create_map(filtered_data, f"Population in {selected_year}")
folium_static(population_map)

# Map 2: Mortality Rate by Country
mortality_data = df[df['Series Name'].str.contains('Mortality rate')]
mortality_data['value'] = mortality_data[selected_year]
mortality_map = create_map(mortality_data, f"Mortality Rate in {selected_year}")
st.header(f"Mortality Rates in {selected_year}")
folium_static(mortality_map)

# Additional visualizations
# Map 3: Urban Population
urban_population_data = df[df['Series Name'] == 'Urban population']
urban_population_data['value'] = urban_population_data[selected_year]
urban_population_map = create_map(urban_population_data, f"Urban Population in {selected_year}")
st.header(f"Urban Population in {selected_year}")
folium_static(urban_population_map)

# Map 4: Life Expectancy
life_expectancy_data = df[df['Series Name'].str.contains('Life expectancy')]
life_expectancy_data['value'] = life_expectancy_data[selected_year]
life_expectancy_map = create_map(life_expectancy_data, f"Life Expectancy in {selected_year}")
st.header(f"Life Expectancy in {selected_year}")
folium_static(life_expectancy_map)

# Map 5: Total Population
total_population_data = df[df['Series Name'] == 'Population, total']
total_population_data['value'] = total_population_data[selected_year]
total_population_map = create_map(total_population_data, f"Total Population in {selected_year}")
st.header(f"Total Population in {selected_year}")
folium_static(total_population_map)

st.sidebar.write("Data visualized using Folium and Streamlit. Please select different options to explore.")
