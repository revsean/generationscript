import requests
import pandas as pd
import base64
import csv
import os

API_BASE_URL = "https://api.planningcenteronline.com/"
APP_ID = "YOUR_APP_ID"
SECRET = "YOUR_SECRET"

def get_pco_data():
    auth_string = f"{APP_ID}:{SECRET}"
    auth_encoded = base64.b64encode(auth_string.encode("utf-8")).decode("utf-8")

    headers = {
        "Authorization": f"Basic {auth_encoded}",
        "Content-Type": "application/json",
    }
    
    # Get groups
    groups_url = f"{API_BASE_URL}groups/v2/groups"
    groups_response = requests.get(groups_url, headers=headers)
    print(f"Groups response: {groups_response.status_code}, {groups_response.text}")
    
    if groups_response.status_code != 200:
        print(f"Error getting groups: {groups_response.status_code}, {groups_response.text}")
        return []
    
    groups = groups_response.json()["data"]
    
    results = []

    for group in groups:
        group_id = group["id"]
        group_name = group["attributes"]["name"]

        # Get leaders
        leaders_url = f"{API_BASE_URL}groups/v2/groups/{group_id}/leaders"
        leaders_response = requests.get(leaders_url, headers=headers)
        print(f"Leaders response for group {group_id}: {leaders_response.status_code}, {leaders_response.text}")
        
        if leaders_response.status_code != 200:
            print(f"Error getting leaders for group {group_id}: {leaders_response.status_code}, {leaders_response.text}")
            continue

        leaders = leaders_response.json()["data"]

        for leader in leaders:
            leader_name = leader["attributes"]["name"]
            leader_email = leader["attributes"]["email"]

            # Get members
            members_url = f"{API_BASE_URL}groups/v2/groups/{group_id}/memberships"
            members_response = requests.get(members_url, headers=headers)
            print(f"Members response for group {group_id}: {members_response.status_code}, {members_response.text}")

            if members_response.status_code != 200:
                print(f"Error getting members for group {group_id}: {members_response.status_code}, {members_response.text}")
                continue

            members = members_response.json()["data"]
            member_count = len(members)

            results.append({
                "Group Name": group_name,
                "Group Leader Name": leader_name,
                "Group Leader Email": leader_email,
                "Number of People in Group": member_count
            })

    return results

def export_to_csv(data, filename):
    if not data:
        print("No data to export.")
        return

    with open(filename, "w", newline="", encoding="utf-8") as csvfile:
        fieldnames = ["Group Name", "Group Leader Name", "Group Leader Email", "Number of People in Group"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()
        for row in data:
            writer.writerow(row)

    # Ensure the file exists and has content
    if not os.path.exists(filename) or os.path.getsize(filename) == 0:
        print(f"File {filename} not found or is empty. Creating an empty file.")
        with open(filename, "w", newline="", encoding="utf-8") as csvfile:
            csvfile.write("")

    print(f"Data exported to {filename}")


def main():
    data = get_pco_data()
    csv_file_path = os.path.join(os.getcwd(), "pco_data.csv")
    export_to_csv(data, csv_file_path)
    print(f"CSV file generated at: {csv_file_path}")

if __name__ == "__main__":
    main()
