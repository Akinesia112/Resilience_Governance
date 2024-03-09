import os
import pandas as pd
from pyproj import Proj, Transformer

# Define the directory path containing the CSV files
directory_path = r"C:\Users\Acer\Downloads\socialfacilities"

# Define the coordinate systems for the transformation using Transformer
transformer = Transformer.from_crs("epsg:3826", "epsg:4326", always_xy=True)

# Loop through each file in the directory
for filename in os.listdir(directory_path):
    if filename.endswith(".csv"):  # Check if the file is a CSV
        file_path = os.path.join(directory_path, filename)
        
        # Load the CSV file
        data = pd.read_csv(file_path)

        # Apply the transformation
        data[['X坐標_transformed', 'Y坐標_transformed']] = data.apply(
            lambda row: transformer.transform(row['X坐標'], row['Y坐標']), axis=1, result_type="expand"
        )

        # Delete the original coordinate columns
        data.drop(['X坐標', 'Y坐標'], axis=1, inplace=True)

        # Rename the transformed columns
        data.rename(columns={'X坐標_transformed': 'X坐標', 'Y坐標_transformed': 'Y坐標'}, inplace=True)

        # Optionally, you can save the modified DataFrame to a new file
        # or overwrite the original file by using the same 'file_path'
        output_file_path = file_path  # Or specify a new file path
        data.to_csv(output_file_path, index=False, encoding='utf-8-sig')

        print(f"Data processed and saved to {output_file_path}")
    else:
        continue  # Skip non-CSV files
