import os
import requests
from datetime import datetime

# Replace with your PCO API credentials
app_id = os.environ['PCO_APP_ID']
app_secret = os.environ['PCO_APP_SECRET']

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

# Function to retrieve all people with pagination
def get_all_people():
    params = {
        'include': 'field_data',
        'per_page': 100,
        'page': 1,
    }
    all_people = []

    while True:
        people_page = query_pco_api(people_endpoint, params)
        all_people.extend(people_page['data'])

        if 'next' in people_page['links']:
            params['page'] += 1
        else:
            break

    return all_people

# Get all people
people = get_all_people()

# Get field definitions
field_defs = query_pco_api(field_defs_endpoint)

# Find the ID of the custom field 'Generation' in the 'General' tab
generation_field_id = None
for field_def in field_defs['data']:
    if field_def['attributes']['name'] == 'Generation' and field_def['attributes']['tab'] == 'General':
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
for person in people:
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
