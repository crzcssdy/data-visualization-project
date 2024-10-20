# Import BigQuery API and setup access
from google.cloud import bigquery
from google.oauth2 import service_account
import json
credentials = service_account.Credentials.from_service_account_file(
'config.json')

client = bigquery.Client(credentials= credentials)

query = """
    SELECT year, country_name, indicator_name, value
    FROM `bigquery-public-data.world_bank_wdi.indicators_data`
    WHERE indicator_name IN (
            'GDP per capita (current US$)',
            'Fertility rate, total (births per woman)',
            'Urban population',
            'Rural population')
    ORDER BY year DESC, country_name, indicator_name
"""
rows = client.query_and_wait(query)  # Make an API request.

results = []
for row in rows:
    results.append(row.values())

# Set variables to track country and year as we loop through list results
previous_year_value = 0
previous_country = ""
# Set dictionaries and lists to hold the values
year_dict = {}
country_entry = {}
metrics_dict = {}
country_list = []

for row in results:
    # Account for last line in rows
    if row == results[-1]:
        if metrics_dict != {}:
            metrics_dict[row[2]] = row[3] 
            country_entry['Metrics'] = metrics_dict
            country_list.append(country_entry)
            # Clear out country_entry and metrics_dict
            country_entry = {}
            metrics_dict = {}
            # Add country_list as a year entry in year_dict
            year_dict[previous_year_value] = country_list
            country_list = []
    elif row[0] != previous_year_value:
        # If country_entry and metrics_dict are not null, add them to country_list
        if country_entry != {} and metrics_dict != {}:
            # Since we've reached the end of the entries for that country we can now add metrics_dict to country_entry
            # and append country_entry to country_list
            country_entry['Metrics'] = metrics_dict
            country_list.append(country_entry)
            # Clear out country_entry and metrics_dict to receive new data
            country_entry = {}
            metrics_dict = {}
            # Add country_list as a year entry in year_dict
            year_dict[previous_year_value] = country_list
            country_list = []
    
    # Check if the current row's value for country is the same as the previous row
    if row[1] != previous_country:
        # If not, we can now add metrics_dict as a value in country_entry and append country_entry to country_list
        if metrics_dict != {}:
            country_entry['Metrics'] = metrics_dict
            country_list.append(country_entry)
            # Clear out country_entry and metrics_dict
            country_entry = {}
            metrics_dict = {}
        # Add new country and metrics data
        country_entry['country'] = row[1]
        metrics_dict[row[2]] = row[3]
        
    else:
        # If the current row's value for country is the same and the previous row, add value to metrics_dict
        metrics_dict[row[2]] = row[3]      
    
    previous_country = row[1]            
    previous_year_value = row[0]   

with open("data.json", "w") as outfile:
    json.dump(year_dict, outfile, indent=2)
