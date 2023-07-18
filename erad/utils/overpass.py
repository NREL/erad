import json
from typing import List

import overpass
import polars

# Define your polygon coordinates as a string

GROCERY_TAGS = [
    'shop=supermarket', 'shop=grocery', 'shop=convenience',
    'shop=market', 'shop=healthfood', 'shop=organic'
]

HOSPITAL_TAGS = [
        'amenity=hospital', 'healthcare=hospital', 'building=hospital',
        'amenity=clinic', 'healthcare=centre','healthcare=pharmacy',
]


def export_json(json_parcels, out_path):
    with open(out_path, 'w') as fp:
        json.dump(json_parcels, fp)

def export_csv(json_parcels, out_path:str):

    csv_data = {
        "id": [],
        "longitude": [],
        "latitude": [],
    }

    for feature in json_parcels['features']:
        for key in  feature['properties']:
            if key not in csv_data:
                csv_data[key] = []
    
    
    for feature in json_parcels['features']:
        csv_data["id"].append(feature["id"])
        csv_data["longitude"].append(feature["geometry"]["coordinates"][0])
        csv_data["latitude"].append(feature["geometry"]["coordinates"][1])

        for key in csv_data:
            if key not in ["id", "longitude", "latitude"]:
                csv_data[key].append(feature['properties'].get(key, None))

    df = polars.from_dict(csv_data)
    df.write_csv(out_path)


def get_sites(polygon: str, tags: List[str] ):
    # polygon = "33.6812,-118.5966, 34.3407,-118.1390" latitude, longitude 
    json_parcels = {
        "type": "FeatureCollection",
        "features": []
    }

    for tag in tags:

        query = f"""
        node[{tag}]({polygon});
        out;
        """

        # Create an instance of the Overpass API
        api = overpass.API()

        # Send the query and retrieve the data
        response = api.Get(query)

        json_parcels['features'].extend(response['features'])
        print(f'Number of parcels extracted of shop type {tag}: ', len(response['features']))

    print('Number of parcels extracted: ', len(json_parcels['features']))
    return json_parcels

