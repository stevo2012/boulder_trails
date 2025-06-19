import pandas as pd
import folium
import numpy as np

# Load your data
df = pd.read_csv('/Users/stephen/Desktop/Strava_Garmin/Boulder Trails/trail_air_weather_gps.csv')

# Debug: Check the data structure
print("Data shape:", df.shape)
print("\nColumn names:", df.columns.tolist())
print("\nFirst few rows:")
print(df.head())
print("\nLat/Long data types:")
print(f"Latitude: {df['latitude'].dtype}, Longitude: {df['longitude'].dtype}")
print("\nLat/Long sample values:")
print(df[['name', 'latitude', 'longitude']].head())
print("\nAny null coordinates?")
print(f"Latitude nulls: {df['latitude'].isnull().sum()}")
print(f"Longitude nulls: {df['longitude'].isnull().sum()}")

# Clean coordinates - ensure they're numeric
df['latitude'] = pd.to_numeric(df['latitude'], errors='coerce')
df['longitude'] = pd.to_numeric(df['longitude'], errors='coerce')

# Remove rows with invalid coordinates
df_clean = df.dropna(subset=['latitude', 'longitude'])
print(f"\nRows after cleaning coordinates: {len(df_clean)}")

# Group by trailhead to get total usage per location
trail_usage = df_clean.groupby(['name', 'latitude', 'longitude']).agg({
    'visits': 'sum'
}).reset_index()

print(f"\nUnique trail locations: {len(trail_usage)}")
print("\nCoordinate ranges:")
print(f"Latitude: {trail_usage['latitude'].min():.4f} to {trail_usage['latitude'].max():.4f}")
print(f"Longitude: {trail_usage['longitude'].min():.4f} to {trail_usage['longitude'].max():.4f}")

# Calculate usage percentages
trail_usage['usage_percentage'] = (trail_usage['visits'] / trail_usage['visits'].sum()) * 100

# Create base map - adjust center based on actual data
if len(trail_usage) > 0:
    center_lat = trail_usage['latitude'].mean()
    center_lon = trail_usage['longitude'].mean()
    print(f"\nMap center: {center_lat:.4f}, {center_lon:.4f}")
else:
    center_lat, center_lon = 40.0150, -105.2705
    print("No valid coordinates found, using default Boulder center")

m = folium.Map(
    location=[center_lat, center_lon], 
    zoom_start=11,
    tiles='OpenStreetMap'
)

# Define color scale based on usage percentage
def get_color(usage_pct):
    if usage_pct > 15:
        return 'red'
    elif usage_pct > 10:
        return 'orange'
    elif usage_pct > 5:
        return 'yellow'
    else:
        return 'blue'

# Add markers for each trailhead
markers_added = 0
for idx, row in trail_usage.iterrows():
    # Validate coordinates are reasonable for Boulder area
    if (39.5 <= row['latitude'] <= 40.5) and (-106.0 <= row['longitude'] <= -104.5):
        folium.CircleMarker(
            location=[row['latitude'], row['longitude']],
            radius=max(8, row['usage_percentage'] * 1.5),  # Increased min size
            popup=f"<b>{row['name']}</b><br>Total Visits: {row['visits']:,}<br>Usage: {row['usage_percentage']:.1f}% of all trail visits",
            tooltip=f"{row['name']}: {row['usage_percentage']:.1f}%",
            color=get_color(row['usage_percentage']),
            fill=True,
            fillOpacity=0.7,
            weight=2
        ).add_to(m)
        markers_added += 1
    else:
        print(f"Skipping {row['name']} - coordinates outside Boulder area: {row['latitude']}, {row['longitude']}")

print(f"\nMarkers added to map: {markers_added}")
print(f"Expected markers: {len(trail_usage)}")

# Add a legend with proper sizing
legend_html = '''
<div style="position: fixed; 
            bottom: 50px; left: 50px; width: 140px; height: 160px; 
            background-color: white; border:2px solid grey; z-index:9999; 
            font-size:12px; padding: 15px; box-shadow: 0 0 15px rgba(0,0,0,0.2);">
<p style="margin: 0 0 8px 0; font-weight: bold;">Trail Usage</p>
<p style="margin: 2px 0;"><span style="color:red; font-size:16px;">●</span> &nbsp;>15%</p>
<p style="margin: 2px 0;"><span style="color:orange; font-size:16px;">●</span> &nbsp;10-15%</p>
<p style="margin: 2px 0;"><span style="color:gold; font-size:16px;">●</span> &nbsp;5-10%</p>
<p style="margin: 2px 0;"><span style="color:blue; font-size:16px;">●</span> &nbsp;<5%</p>
</div>
'''
m.get_root().html.add_child(folium.Element(legend_html))

# Save the map
m.save('boulder_trails_usage_map.html')

print(f"Map saved as 'boulder_trails_usage_map.html'")
print(f"Total trails: {len(trail_usage)}")
print(f"Top 5 most visited trails:")
print(trail_usage.nlargest(5, 'visits')[['name', 'visits', 'usage_percentage']])