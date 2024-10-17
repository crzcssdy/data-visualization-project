from google.cloud import bigquery
from google.oauth2 import service_account
credentials = service_account.Credentials.from_service_account_file(r'C:\Users\jwidc\Desktop\data-visualization-project\gdp.json')
project_id = 'GDB'
client = bigquery.Client(credentials= credentials,project=project_id)