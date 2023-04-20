import requests
import pandas as pd
import base64

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
# (rest of the script remains the same)
    
    groups = groups_response.json()["data"]
    group_data = []

    for group in groups:
        group_id = group["id"]
        group_name = group["attributes"]["name"]

        # Get group leaders
        leaders_url = f"{API_BASE_URL}{ORGANIZATION}/groups/v2/groups/{group_id}/leaders"
        leaders_response = requests.get(leaders_url, headers=headers)
        print(f"Leaders response for group {group_id}: {leaders_response.status_code}, {leaders_response.text}")

        
        if leaders_response.status_code != 200:
            print(f"Error getting group leaders: {leaders_response.status_code}, {leaders_response.text}")
            continue
        
        leaders = leaders_response.json()["data"]

        for leader in leaders:
            leader_id = leader["id"]
            leader_name = leader["attributes"]["name"]
            leader_email = leader["attributes"]["email"]

            # Get the number of people in the group
            members_url = f"{API_BASE_URL}{ORGANIZATION}/groups/v2/groups/{group_id}/memberships"
            members_response = requests.get(members_url, headers=headers)
            print(f"Members response for group {group_id}: {members_response.status_code}, {members_response.text}")

            if members_response.status_code != 200:
                print(f"Error getting group members: {members_response.status_code}, {members_response.text}")
                continue
            
            member_count = len(members_response.json()["data"])

            group_data.append({
                "Group Name": group_name,
                "Group Leader": leader_name,
                "Group Leader Email": leader_email,
                "Group Member Count": member_count,
            })

    return group_data

def main():
    data = get_pco_data()
    df = pd.DataFrame(data)
    df.to_csv("pco_data.csv", index=False)

if __name__ == "__main__":
    main()
