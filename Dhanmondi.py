import requests
import pandas as pd
import folium
from folium.plugins import MarkerCluster

def get_nearby_places(latitude, longitude, radius_meters, amenity_type):
    """
    Fetches nearby places from the Overpass API based on an amenity type.
    """
    overpass_url = "https://overpass-api.de/api/interpreter"
    overpass_query = f"""
    [out:json];
    node(around:{radius_meters},{latitude},{longitude})["amenity"="{amenity_type}"];
    out;
    """
    try:
        response = requests.post(overpass_url, data={'data': overpass_query})
        response.raise_for_status() # Raise an exception for bad status codes
        data = response.json()
        places = []
        for element in data.get('elements', []):
            if 'tags' in element and 'name' in element['tags']:
                places.append({
                    'name': element['tags']['name'],
                    'latitude': element['lat'],
                    'longitude': element['lon']
                })
        return pd.DataFrame(places)
    except requests.exceptions.RequestException as e:
        print(f"Error: API request failed. {e}")
        return pd.DataFrame()

# Set the central coordinates for Dhanmondi, Dhaka and Keari Plaza
dhanmondi_lat, dhanmondi_lon = 23.74, 90.385
keari_plaza_lat, keari_plaza_lon = 23.7485, 90.3705
radius_meters = 1500 # Search radius of 1.5 km

# Fetch different types of businesses
print("Fetching restaurants...")
restaurants = get_nearby_places(dhanmondi_lat, dhanmondi_lon, radius_meters, "restaurant")
print("Fetching cafes...")
cafes = get_nearby_places(dhanmondi_lat, dhanmondi_lon, radius_meters, "cafe")
print("Fetching hotels...")
hotels = get_nearby_places(dhanmondi_lat, dhanmondi_lon, radius_meters, "hotel")

# Create a new map centered on Dhanmondi
map_dhanmondi = folium.Map(location=[dhanmondi_lat, dhanmondi_lon], zoom_start=15)

# Use MarkerCluster to group markers for better performance and readability
restaurants_cluster = MarkerCluster(name='Restaurants').add_to(map_dhanmondi)
cafes_cluster = MarkerCluster(name='Cafes').add_to(map_dhanmondi)
hotels_cluster = MarkerCluster(name='Hotels').add_to(map_dhanmondi)

# Add restaurant markers to the cluster
for idx, row in restaurants.iterrows():
    folium.Marker(
        location=[row['latitude'], row['longitude']],
        popup=f"<b>Restaurant:</b> {row['name']}",
        icon=folium.Icon(color='blue', icon='cutlery', prefix='fa')
    ).add_to(restaurants_cluster)

# Add cafe markers to the cluster
for idx, row in cafes.iterrows():
    folium.Marker(
        location=[row['latitude'], row['longitude']],
        popup=f"<b>Cafe:</b> {row['name']}",
        icon=folium.Icon(color='green', icon='coffee', prefix='fa')
    ).add_to(cafes_cluster)

# Add hotel markers to the cluster
for idx, row in hotels.iterrows():
    folium.Marker(
        location=[row['latitude'], row['longitude']],
        popup=f"<b>Hotel:</b> {row['name']}",
        icon=folium.Icon(color='purple', icon='bed', prefix='fa')
    ).add_to(hotels_cluster)

# HIGHLIGHT THE MOST IMPORTANT PART: Dhanmondi 15 Keari Plaza
# A separate, custom marker is used to make it stand out
folium.Marker(
    location=[keari_plaza_lat, keari_plaza_lon],
    popup="<b>Keari Plaza, Dhanmondi 15</b>",
    tooltip="Keari Plaza",
    icon=folium.Icon(color='red', icon='star', prefix='fa')
).add_to(map_dhanmondi)

# Add a layer control to toggle clusters on/off
folium.LayerControl().add_to(map_dhanmondi)

# Save the map as an HTML file or display in a notebook
map_dhanmondi.save("dhanmondi_businesses.html")
print("\nMap generated! Check 'dhanmondi_businesses.html' in your directory.")

# In a Jupyter Notebook or Google Colab, simply calling the map object will display it
map_dhanmondi