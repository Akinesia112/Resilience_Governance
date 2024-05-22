import os
import geopandas as gpd
import pandas as pd
from shapely.geometry import box, Point

# Define input and output directory paths
input_directory = r"D:/韌性治理/Google_POI_Geojson"
output_csv_path = r"D:/韌性治理/2024_Taichung_POI_gmap_Grid_Point_Count.csv"
output_geojson_path = r"D:/韌性治理/2024_Taichung_POI_gmap_Grid_Point_Count.geojson"
grid_path = r"D:/韌性治理/Grid/grid.geojson"  # 路径到网格文件

# Load the grid GeoDataFrame
grid_gdf = gpd.read_file(grid_path)

grid_gdf['geometry'] = grid_gdf.apply(lambda row: box(row['left'], row['bottom'], row['right'], row['top']), axis=1)
grid_gdf = gpd.GeoDataFrame(grid_gdf, geometry='geometry', crs='EPSG:3857')

# Ensure grid_gdf has 'grid_index' as an index column
if 'grid_index' not in grid_gdf.columns:
    grid_gdf['grid_index'] = grid_gdf.index

# Get a list of all GeoJSON files in the directory
geojson_files = [f for f in os.listdir(input_directory) if f.endswith('.geojson')]

# Initialize an empty DataFrame to store counts
count_df = pd.DataFrame()

# Process each POI GeoJSON file
for file in geojson_files:
    file_path = os.path.join(input_directory, file)
    poi_gdf = gpd.read_file(file_path)
    
    # Convert lat and lng to Point geometries
    poi_gdf['geometry'] = poi_gdf.apply(lambda row: Point(row['lng'], row['lat']), axis=1)
    poi_gdf = gpd.GeoDataFrame(poi_gdf, geometry='geometry', crs='EPSG:4326')
    
    # Convert to the same CRS as the grid
    poi_gdf = poi_gdf.to_crs(epsg=3857)
    
    print(f"Processing {file} with columns: {poi_gdf.columns.tolist()}")
    
    if 'geometry' not in poi_gdf.columns or poi_gdf['geometry'].isnull().all():
        print(f"Warning: No valid geometry in {file}. Skipping this file.")
        continue

    joined_gdf = gpd.sjoin(grid_gdf, poi_gdf, how="inner", predicate='intersects', lsuffix='grid', rsuffix='poi')
    
    poi_type = file.replace('.geojson', '').replace('Grid_output_', '')
    counts = joined_gdf.groupby('grid_index').agg(point_count=('geometry', 'count')).reset_index()
    counts.rename(columns={'point_count': f'point_count_{poi_type}'}, inplace=True)
    
    print(f"Counts for {file}:\n{counts.head()}")

    if count_df.empty:
        count_df = counts
    else:
        count_df = count_df.merge(counts, on='grid_index', how='outer', suffixes=(None, f'_{poi_type}'))
    
    print(f"Updated count_df after processing {file}:\n{count_df.head()}")

count_df.fillna(0, inplace=True)

final_gdf = grid_gdf[['grid_index', 'geometry']].merge(count_df, on='grid_index')
print(f"Final GeoDataFrame:\n{final_gdf.head()}")

final_gdf.to_file(output_geojson_path, driver='GeoJSON', encoding='utf-8-sig')
print("GeoJSON file saved.")

non_geom_cols = [col for col in final_gdf.columns if col != 'geometry']
final_gdf[non_geom_cols].to_csv(output_csv_path, index=False, encoding='utf-8-sig')
print("CSV file saved.")
