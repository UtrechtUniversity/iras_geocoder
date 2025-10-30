import requests

def get_coordinates(postal_code, house_number,houseletter,houseaddition):
    url = f"https://api.pdok.nl/bzk/locatieserver/search/v3_1/free?q=\"{postal_code} {house_number} {houseletter} {houseaddition}\""
    #print(url)
    response = requests.get(url)

    
    if response.status_code == 200:
        data = response.json()
        docs = data.get("response", {}).get("docs", [])
        
        if docs:
            first_result = docs[0]
            coordinates = first_result.get("centroide_rd")
            
            if coordinates:
                return coordinates
            else:
                return False
        else:
            return False
    else:
        return False
