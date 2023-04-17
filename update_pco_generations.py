import os
import requests
from datetime import datetime

# Replace with your PCO API credentials
app_id = os.environ[dd5393328c2bb9abfaaec29a6028a54440b853eb83d058599a269304074dded0]
app_secret = os.environ[690aa3371090c4fb8032d9d0a781603bf8c3010da65d60fdd1196640cdc2c595]

# Set the API endpoints
base_url = 'https://api.planningcenteronline.com/people/v2'
people_endpoint = f'{base_url}/people'
field_defs_endpoint = f'{base_url}/field_definitions'
field_data_endpoint = lambda person_id: f'{base_url}/people/{person_id}/field_data'

# Query the PCO API
def query_pco_api(endpoint, params=None):
    response = requests.get(
        endpoint,
        auth=(app_id, app_secret),
        headers={'Content-Type': 'application/json'},
        params=params,
    )
    response.raise_for_status()
    return response.json()

# Get people with a birthday today and a blank custom field
params = {
    'where[birthday]': datetime.now().strftime('%m-%d'),
    'include': 'field_data',
}
people = query_pco_api(people_endpoint, params)

# Get field definitions
field_defs = query_pco_api(field_defs_endpoint)

# Find the ID of the custom field 'Generation'
generation_field_id = None
for field_def in field_defs['data']:
    if field_def['attributes']['name'] == 'Generation':
        generation_field_id = field_def['id']
        break

if not generation_field_id:
    raise ValueError("Custom field 'Generation' not found")

# Function to calculate the generation name based on the birth year
def get_generation_name(birth_year):
    if birth_year < 1946:
        return "Lost Generation"
    elif birth_year <= 1964:
        return "Baby Boomers"
    elif birth_year <= 1979:
        return "Generation X"
    elif birth_year <= 1994:
        return "Millennials"
    elif birth_year <= 2012:
        return "Generation Z"
    else:
        return "Generation Alpha"

# Update the custom field for each person
for person in people['data']:
    person_id = person['id']
    birth_year = int(person['attributes']['birthdate'][:4])
    generation_name = get_generation_name(birth_year)

    # Check if the custom field is blank
    field_data = person['relationships']['field_data']['data']
    for field in field_data:
        if field['relationships']['field_definition']['data']['id'] == generation_field_id and not field['attributes']['value']:
            # Update the custom field
            update_url = f"{field_data_endpoint(person_id)}/{field['id']}"
            payload = {
                'data': {
                    'type': 'FieldDatum',
                    'attributes': {
                        'value': generation_name
                    }
                }
            }
            response = requests.patch(update_url, auth=(app_id, app_secret), json=payload)
            response.raise_for_status()
            print(f"Updated generation for person {person_id} to {generation_name}")
