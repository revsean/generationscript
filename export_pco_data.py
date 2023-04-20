import requests
import pandas as pd

API_BASE_URL = "https://api.planningcenteronline.com/"
APP_ID = "YOUR_APP_ID"
SECRET = "YOUR_SECRET"
ORGANIZATION = "O228371"

def get_pco_data():
    headers = {
        "Authorization": f"Basic {APP_ID}:{SECRET}",
        "Content-Type": "application/json",
    }
    
    # Get groups
    groups_url = f"{API_BASE_URL}{ORGANIZATION}/groups/v2/groups"
    groups_response = requests.get(groups_url, headers=headers)
    
    if groups_response.status_code != 200:
        print(f"Error getting groups: {groups_response.status_code}, {groups_response.text}")
        return []
    
    groups = groups_response.json()["data"]
    group_data = []

    for group in groups:
        group_id = group["id"]
        group_name = group["attributes"]["name"]

        # Get group leaders
        leaders_url = f"{API_BASE_URL}{ORGANIZATION}/groups/v2/groups/{group_id}/leaders"
        leaders_response = requests.get(leaders_url, headers=headers)
        
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
