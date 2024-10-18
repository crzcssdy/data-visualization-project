import pandas as pd
import json
import streamlit as st
import plotly.express as px

# Load the data from the JSON file
with open('fertility_gdp_2014_2024.json') as f:
    data = json.load(f)

# Convert the JSON data into a DataFrame
df = pd.DataFrame(data)


# Pivot the data so that each row contains both Fertility Rate and GDP for the same year
df_pivot = df.pivot_table(index=['Country Name', 'Country Code', 'Year'], 
                          columns='Series Name_y', 
                          values='GDP', 
                          aggfunc='first').reset_index()

# Flatten the columns to remove multi-level index
df_pivot.columns.name = None

# Rename columns for easier understanding
df_pivot = df_pivot.rename(columns={
    'GDP per capita (current US$)': 'GDP_per_Capita',
    'GDP per capita growth (annual %)': 'GDP_Growth_Percent'
})

# Also, merge the fertility rate column (which is under "Series Name_x")
fertility_data = df[df['Series Name_x'] == 'Fertility rate. total (births per woman)']
fertility_data = fertility_data[['Country Name', 'Country Code', 'Year', 'Fertility Rate']]

# Merge fertility rate with GDP data
df_merged = pd.merge(df_pivot, fertility_data, on=['Country Name', 'Country Code', 'Year'])

# Ensure GDP Growth Percent is non-negative
df_merged['GDP_Growth_Percent_Abs'] = df_merged['GDP_Growth_Percent'].abs()

# Scatter Plot - Fertility vs GDP
fig = px.scatter(df_merged, x='GDP_per_Capita', y='Fertility Rate', color='Country Code',
                 size='GDP_Growth_Percent_Abs', hover_name='Country Name', 
                 title="Fertility Rate vs GDP Per Capita")
st.plotly_chart(fig)

# Load the processed data (df_merged from the above step)
# Assuming df_merged is already loaded in the session

# Streamlit App Layout
st.title("Global Population Growth and Fertility Trends in Relation to Economic Development")

# Dropdown for selecting the metric (GDP, fertility, or population growth)
metric = st.selectbox("Select Metric to Display", ['GDP per Capita', 'Fertility Rate', 'Population Growth'])

# Choropleth Map
st.subheader(f"Choropleth Map - {metric}")
# Prepare data for the map
if metric == 'GDP per Capita':
    fig = px.choropleth(df_merged, locations='Country Code', color='GDP_per_Capita', hover_name='Country Name',
                        color_continuous_scale=px.colors.sequential.Plasma, title='Global GDP per Capita (2014-2024)')
elif metric == 'Fertility Rate':
    fig = px.choropleth(df_merged, locations='Country Code', color='Fertility Rate', hover_name='Country Name',
                        color_continuous_scale=px.colors.sequential.Plasma, title='Global Fertility Rates (2014-2024)')
else:
    fig = px.choropleth(df_merged, locations='Country Code', color='GDP_Growth_Percent', hover_name='Country Name',
                        color_continuous_scale=px.colors.sequential.Plasma, title='Global Population Growth (2014-2024)')

st.plotly_chart(fig)

# Scatter Plot - Fertility vs GDP
st.subheader("Scatter Plot - Fertility vs GDP")
# Prepare data for scatter plot
fig = px.scatter(df_merged, x='GDP_per_Capita', y='Fertility Rate', color='Country Code', size='GDP_Growth_Percent',
                 hover_name='Country Name', title="Fertility Rate vs GDP Per Capita")
st.plotly_chart(fig)

# Line Chart - Trends over Time
st.subheader("Trends over Time")
# Select countries for comparison
countries = df_merged['Country Name'].unique()
selected_countries = st.multiselect('Select Countries to Compare', countries, default=['Afghanistan', 'Albania', 'Algeria'])

# Filter data for selected countries
df_filtered = df_merged[df_merged['Country Name'].isin(selected_countries)]

fig = px.line(df_filtered, x='Year', y='Fertility Rate', color='Country Name',
              title="Fertility Rate Trends Over Time")
fig.add_scatter(x=df_filtered['Year'], y=df_filtered['GDP_per_Capita'], mode='lines', name='GDP per Capita')

st.plotly_chart(fig)

# Bar Chart - Top 10 and Bottom 10 Countries
st.subheader("Top 10 and Bottom 10 Countries")

# Get top 10 countries by GDP
top_10_gdp = df_merged.groupby('Country Name').agg({'GDP_per_Capita': 'mean'}).nlargest(10, 'GDP_per_Capita')
bottom_10_gdp = df_merged.groupby('Country Name').agg({'GDP_per_Capita': 'mean'}).nsmallest(10, 'GDP_per_Capita')

# Bar charts for top and bottom countries
top_10_gdp_fig = px.bar(top_10_gdp, x=top_10_gdp.index, y='GDP_per_Capita', labels={'GDP_per_Capita': 'GDP per Capita'}, title="Top 10 Countries by GDP")
bottom_10_gdp_fig = px.bar(bottom_10_gdp, x=bottom_10_gdp.index, y='GDP_per_Capita', labels={'GDP_per_Capita': 'GDP per Capita'}, title="Bottom 10 Countries by GDP")

st.plotly_chart(top_10_gdp_fig)
st.plotly_chart(bottom_10_gdp_fig)

# Interactivity: Country Search
st.subheader("Search for a Country")
country_search = st.text_input("Enter a country name:")
if country_search:
    country_data = df_merged[df_merged['Country Name'].str.contains(country_search, case=False)]
    if not country_data.empty:
        st.write(country_data)
    else:
        st.write("No data found for the selected country.")
