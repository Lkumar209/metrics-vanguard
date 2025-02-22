import requests
from PIL import Image
from io import BytesIO

def get_team_logo(team_name, api_key):
    """Fetches the logo of the given soccer team."""
    try:
        # API URL for searching team by name
        url = f"https://www.thesportsdb.com/api/v1/json/{api_key}/searchteams.php?t={team_name}"
        
        # Make a GET request to the API
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        # Check if the team is found
        if data["teams"]:
            team = data["teams"][0]  # Get the first result
            logo_url = team["strTeamBadge"]  # Logo URL

            if logo_url:
                # Fetch and display the logo
                logo_response = requests.get(logo_url)
                logo_response.raise_for_status()
                logo_image = Image.open(BytesIO(logo_response.content))

                print(f"Logo of {team_name}:")
                logo_image.show()
            else:
                print("Logo not available for this team.")
        else:
            print("Team not found.")

    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")

# Main execution
if __name__ == "__main__":
    api_key = "3"  # Replace with your API key from SportsDB
    team_name = input("Enter the soccer team name: ")
    get_team_logo(team_name, api_key)
