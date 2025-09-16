import requests

mapping = {
    "Delhi" : "Gateway of India",
    "Hyderabad" : "Taj Mahal",
    "New York" : "Eiffel Tower",
    "Istanbul" : "Big Ben"
}

def _get_favorite_city() -> str:
        """Step 1: Get favorite city from API"""
        try:
            # Replace with actual endpoint URL
            url = "https://register.hackrx.in/submissions/myFavouriteCity"
            
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                data = response.json()
                # Assuming the API returns {"city": "CityName"} or similar
                city = data.get('data').get('city')
                if city:
                    return city.strip()
                else:
                    # If it's just a string response
                    return response.text.strip().strip('"')
            else:
                return None
        except Exception as e:
            return None
    
def get_flight_number(landmark: str) -> str:
    if landmark in mapping:
        if mapping[landmark] == "Gateway of India":
            res = requests.get("https://register.hackrx.in/teams/public/flights/getFirstCityFlightNumber")
            return res.json().get('data').get('flightNumber')
        elif mapping[landmark] == "Taj Mahal":
            res = requests.get("https://register.hackrx.in/teams/public/flights/getSecondCityFlightNumber")
            return res.json().get('data').get('flightNumber')
        elif mapping[landmark] == "Eiffel Tower":
            res = requests.get("https://register.hackrx.in/teams/public/flights/getThirdCityFlightNumber")
            return res.json().get('data').get('flightNumber')
        elif mapping[landmark] == "Big Ben":
            res = requests.get("https://register.hackrx.in/teams/public/flights/getFourthCityFlightNumber")
            return res.json().get('data').get('flightNumber')
    else:
        res = requests.get("https://register.hackrx.in/teams/public/flights/getFifthCityFlightNumber")
        return res.json().get('data').get('flightNumber')
        
fav_city = _get_favorite_city()

number = get_flight_number(fav_city)

print(number)
