# Extracts the data, processes and stores them in a matrix formart for each ward separately in a directory
import os
import geopandas as gpd
import xarray as xr
import rioxarray
import pandas as pd
from shapely.geometry import mapping

#replaces any characters in the file name that are not alphanumeric 
def sanitize_filename(filename):
    return "".join(char if char.isalnum() or char in (' ', '_') else '_' for char in filename)

#Creates a string for the naming convention of the dekads based on months 
def get_dekad_name(month, dekad_number):
    month_names = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    dekads = ['dk1', 'dk2', 'dk3']
    return f"{month_names[month-1]}-{dekads[dekad_number-1]}"
# Main function for processing soil moisture data 
def create_daily_soil_moisture(base_dir, shapefile_path, start_year, end_year):
    
    # Load kenya level 3 Shapefile
    wards = gpd.read_file(shapefile_path)
    print(f"Shapefile loaded: {len(wards)} wards found.")

    # Initialize dictionary to store data for each ward and categorises
    dekads = [f"{month}-{dk}" for month in ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'] for dk in ['dk1', 'dk2', 'dk3']]
    ward_data = {ward.NAME_3: pd.DataFrame(index=dekads) for ward in wards.itertuples()}

    # Iterate through each year
    for year in range(start_year, end_year + 1):
        year_dir = os.path.join(base_dir, str(year))
        if not os.path.isdir(year_dir):
            print(f"Year directory not found: {year_dir}")
            continue
        # progress Tracking
        print(f"Processing year: {year}")

        # Iterate over each month directory within the selected year
        for month_dir in sorted(os.listdir(year_dir)):
            month_path = os.path.join(year_dir, month_dir)

            # Check if it's a directory
            if not os.path.isdir(month_path):
                continue  # Skip if it's not a directory

            # Create a list of nc file paths within that month
            data_files = [f for f in os.listdir(month_path) if f.endswith('.nc')]
            if not data_files:
                print(f"No .nc files found in {month_path}")
                continue

            # Loop through each data file, open dataset, and process dekad data
            for data_file in data_files:
                file_path = os.path.join(month_path, data_file)
                print(f"Processing file: {file_path}")

                try:
                    data = xr.open_dataset(file_path)
                    data.rio.set_spatial_dims(x_dim='lon', y_dim='lat', inplace=True)
                    data.rio.write_crs('epsg:4326', inplace=True)
                except Exception as e:
                    print(f"Error reading data file {file_path}: {e}")
                    continue

                # Determine dekad based on file name (file names follow a simillar pattern)
                dekad_number = int(data_file.split('-dk')[-1][0])
                dekad_name = get_dekad_name(int(month_dir), dekad_number)

                # Clip data to Kenya boundary using Level 3 shapefile
                clipped_data = data['sm_c4grass'].rio.clip(wards.geometry.apply(mapping), wards.crs, drop=True)

                # Append data for each ward to the list for dekad data
                for ward in wards.itertuples():
                    ward_name = ward.NAME_3
                    try:
                        soil_moisture_value = clipped_data.sel(lon=ward.geometry.centroid.x, lat=ward.geometry.centroid.y, method='nearest').item()
                        ward_data[ward_name].loc[dekad_name, year] = soil_moisture_value
                    except KeyError:
                        print(f"Data missing for ward {ward_name} on {dekad_name}")

    # Save each ward's data to separate Excel files
    output_dir = r'E:\Python\GeoPandas\WardOutput'  
    os.makedirs(output_dir, exist_ok=True)

    for ward_name, data_df in ward_data.items():
        if data_df.empty:
            print(f"No data for ward {ward_name}. Skipping file creation.")
            continue
        sanitized_ward_name = sanitize_filename(ward_name)
        ward_output_dir = os.path.join(output_dir, sanitized_ward_name)
        os.makedirs(ward_output_dir, exist_ok=True)
        excel_path = os.path.join(ward_output_dir, f"{sanitized_ward_name}_Daily_Soil_Moisture.xlsx")
        # Writing  the DataFrame to Excel file using dekads as the index 
        data_df.to_excel(excel_path, index=True)
        print(f"Daily soil moisture data for {ward_name} saved to {excel_path}")

# Parameters fo functions used
base_dir = r'E:\Python\GeoPandas\Tamstat_data'
shapefile_path = r'E:\Python\GeoPandas\gadm41_KEN_shp\gadm41_KEN_3.shp'
start_year = 1983
end_year = 2024

# Create daily soil moisture data
create_daily_soil_moisture(base_dir, shapefile_path, start_year, end_year)
