import pandas as pd
import matplotlib.pyplot as plt
import contextily as ctx
import geopandas as gpd
from shapely.geometry import Point
import numpy as np

# Load your data
df = pd.read_csv('/Users/stephen/Desktop/Strava_Garmin/Boulder Trails/trail_air_weather_gps.csv')

# Clean coordinates
df['latitude'] = pd.to_numeric(df['latitude'], errors='coerce')
df['longitude'] = pd.to_numeric(df['longitude'], errors='coerce')
df_clean = df.dropna(subset=['latitude', 'longitude'])

# Group by trailhead to get total usage per location
trail_usage = df_clean.groupby(['name', 'latitude', 'longitude']).agg({
    'visits': 'sum'
}).reset_index()

# Calculate usage percentages
trail_usage['usage_percentage'] = (trail_usage['visits'] / trail_usage['visits'].sum()) * 100

# Create GeoDataFrame for trails
geometry = [Point(lon, lat) for lon, lat in zip(trail_usage['longitude'], trail_usage['latitude'])]
gdf_trails = gpd.GeoDataFrame(trail_usage, geometry=geometry, crs='EPSG:4326')

# Get Boulder city boundary
try:
    # Download city boundaries (this downloads US places data)
    places = gpd.read_file('https://www2.census.gov/geo/tiger/GENZ2020/shp/cb_2020_08_place_500k.zip')
    boulder_city = places[places['NAME'] == 'Boulder']
    
    if len(boulder_city) == 0:
        print("Boulder city boundary not found, using trail extent")
        boulder_city = None
    else:
        print("Boulder city boundary loaded successfully")
except Exception as e:
    print(f"Could not download city boundaries: {e}")
    print("Using trail extent instead")
    boulder_city = None

# Convert to Web Mercator for plotting
gdf_trails_web = gdf_trails.to_crs(epsg=3857)
if boulder_city is not None:
    boulder_city_web = boulder_city.to_crs(epsg=3857)

# Create the plot
fig, ax = plt.subplots(figsize=(12, 10))

# Plot city boundary first (if available)
if boulder_city is not None:
    boulder_city_web.boundary.plot(ax=ax, color='darkgreen', linewidth=3, alpha=0.9)
    boulder_city_web.plot(ax=ax, color='lightgreen', alpha=0.15)
    # Set extent to city bounds with padding
    bounds = boulder_city_web.total_bounds
    padding = (bounds[2] - bounds[0]) * 0.1  # 10% padding to show surrounding area
    ax.set_xlim(bounds[0] - padding, bounds[2] + padding)
    ax.set_ylim(bounds[1] - padding, bounds[3] + padding)
else:
    # Fallback: use trail locations to set bounds
    bounds = gdf_trails_web.total_bounds
    padding = (bounds[2] - bounds[0]) * 0.2
    ax.set_xlim(bounds[0] - padding, bounds[2] + padding)
    ax.set_ylim(bounds[1] - padding, bounds[3] + padding)

# Plot trail points
scatter = ax.scatter(gdf_trails_web.geometry.x, gdf_trails_web.geometry.y, 
                    s=trail_usage['usage_percentage'] * 30,  # Larger for city view
                    c=trail_usage['usage_percentage'], 
                    alpha=0.8, cmap='YlOrRd', edgecolors='black', linewidth=0.8,
                    zorder=5)  # Ensure points are on top

# Add basemap - using satellite imagery for better detail
ctx.add_basemap(ax, crs=gdf_trails_web.crs, source=ctx.providers.Esri.WorldImagery)

# Add colorbar
cbar = plt.colorbar(scatter, ax=ax, shrink=0.7, pad=0.02)
cbar.set_label('Trail Usage (%)', rotation=270, labelpad=20, fontsize=12)

# Formatting
ax.set_xlabel('')
ax.set_ylabel('')
ax.set_title('Boulder City Trail Usage Distribution', fontsize=18, fontweight='bold', pad=20)

# Remove axis ticks
ax.set_xticks([])
ax.set_yticks([])

# Add city label if boundary was found
if boulder_city is not None:
    ax.text(0.02, 0.98, 'City of Boulder, Colorado', transform=ax.transAxes, 
            fontsize=12, verticalalignment='top', 
            bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))

plt.tight_layout()
plt.savefig('boulder_city_trails_map.png', dpi=300, bbox_inches='tight', 
            facecolor='white', edgecolor='none')
plt.show()

print("City map saved as 'boulder_city_trails_map.png'")
print(f"Total trails plotted: {len(trail_usage)}")
if boulder_city is not None:
    print("Boulder city boundary included")
else:
    print("City boundary not available - showing trail area only")
trail_usage = df_clean.groupby(['name', 'latitude', 'longitude']).agg({
    'visits': 'sum'
}).reset_index()

# Calculate usage percentages
trail_usage['usage_percentage'] = (trail_usage['visits'] / trail_usage['visits'].sum()) * 100

# Create GeoDataFrame for trails
geometry = [Point(lon, lat) for lon, lat in zip(trail_usage['longitude'], trail_usage['latitude'])]
gdf_trails = gpd.GeoDataFrame(trail_usage, geometry=geometry, crs='EPSG:4326')

# Get Boulder County boundary
try:
    # Download county boundaries (this downloads US county data)
    counties = gpd.read_file('https://www2.census.gov/geo/tiger/GENZ2020/shp/cb_2020_us_county_20m.zip')
    boulder_county = counties[(counties['NAME'] == 'Boulder') & (counties['STATEFP'] == '08')]
    
    if len(boulder_county) == 0:
        print("Boulder County boundary not found, using trail extent")
        boulder_county = None
except:
    print("Could not download county boundaries, using trail extent")
    boulder_county = None

# Convert to Web Mercator for plotting
gdf_trails_web = gdf_trails.to_crs(epsg=3857)
if boulder_county is not None:
    boulder_county_web = boulder_county.to_crs(epsg=3857)

# Create the plot
fig, ax = plt.subplots(figsize=(12, 10))

# Plot county boundary first (if available)
if boulder_county is not None:
    boulder_county_web.boundary.plot(ax=ax, color='navy', linewidth=2, alpha=0.8)
    boulder_county_web.plot(ax=ax, color='lightblue', alpha=0.1)
    # Set extent to county bounds with some padding
    bounds = boulder_county_web.total_bounds
    padding = (bounds[2] - bounds[0]) * 0.05  # 5% padding
    ax.set_xlim(bounds[0] - padding, bounds[2] + padding)
    ax.set_ylim(bounds[1] - padding, bounds[3] + padding)

# Plot trail points
scatter = ax.scatter(gdf_trails_web.geometry.x, gdf_trails_web.geometry.y, 
                    s=trail_usage['usage_percentage'] * 25,  # Slightly larger for county view
                    c=trail_usage['usage_percentage'], 
                    alpha=0.8, cmap='YlOrRd', edgecolors='black', linewidth=0.8,
                    zorder=5)  # Ensure points are on top

# Add basemap - using a more detailed terrain map
ctx.add_basemap(ax, crs=gdf_trails_web.crs, source=ctx.providers.Esri.WorldTopoMap)

# Add colorbar
cbar = plt.colorbar(scatter, ax=ax, shrink=0.7, pad=0.02)
cbar.set_label('Trail Usage (%)', rotation=270, labelpad=20, fontsize=12)

# Formatting
ax.set_xlabel('')
ax.set_ylabel('')
ax.set_title('Boulder County Trail Usage Distribution', fontsize=18, fontweight='bold', pad=20)

# Remove axis ticks
ax.set_xticks([])
ax.set_yticks([])

# Add county label if boundary was found
if boulder_county is not None:
    ax.text(0.02, 0.98, 'Boulder County, Colorado', transform=ax.transAxes, 
            fontsize=12, verticalalignment='top', 
            bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))

plt.tight_layout()
plt.savefig('boulder_county_trails_map.png', dpi=300, bbox_inches='tight', 
            facecolor='white', edgecolor='none')
plt.show()

print("County map saved as 'boulder_county_trails_map.png'")
print(f"Total trails plotted: {len(trail_usage)}")
if boulder_county is not None:
    print("Boulder County boundary included")