import geopandas as gpd
import pandas as pd
import folium

# Load Boulder County boundary
boulder = gpd.read_file("/Users/stephen/Desktop/Strava_Garmin/Boulder Trails/Colorado_County_Boundaries.geojson")  # <- Replace with actual path

# Load trailhead CSV (must contain 'latitude' and 'longitude' columns)
trailheads = pd.read_csv("/Users/stephen/Desktop/Strava_Garmin/Boulder Trails/trail_air_weather_gps.csv")  # <- Replace with your file

# Create a base map centered on Boulder
m = folium.Map(location=[40.015, -105.2705], zoom_start=11)

# Add county border
folium.GeoJson(boulder).add_to(m)

# Add trailheads
for _, row in trailheads.iterrows():
    folium.Marker(
        location=[row['latitude'], row['longitude']],
        popup=row.get('name', 'Trailhead'),
        icon=folium.Icon(color='green', icon='tree-conifer', prefix='glyphicon')
    ).add_to(m)

# Save map
m.save("boulder_trailhead_map.html")
