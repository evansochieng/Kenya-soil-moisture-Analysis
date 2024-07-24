import os
import geopandas as gpd
import xarray as xr
import rioxarray
import pandas as pd
from shapely.geometry import mapping

def sanitize_filename(filename):
    # Replace invalid characters with underscores
    return "".join(char if char.isalnum() or char in (' ', '_') else '_' for char in filename)

def create_daily_soil_moisture(base_dir, shapefile_path, start_year, end_year):
    # Load Shapefile
    wards = gpd.read_file(shapefile_path)
    
    # Initialize dictionary to store data for each ward
    ward_data = {ward.NAME_3: [] for ward in wards.itertuples()}

    # Iterate through each year
    for year in range(start_year, end_year + 1):
        year_dir = os.path.join(base_dir, str(year))
        if not os.path.isdir(year_dir):
            continue

        print(f"Processing year: {year}")

        # Iterate over each month directory within the selected year
        for month_dir in sorted(os.listdir(year_dir)):
            month_path = os.path.join(year_dir, month_dir)

            # Check if it's a directory
            if not os.path.isdir(month_path):
                continue  # Skip if it's not a directory

            # Create a list of nc file paths within that month
            data_files = [f for f in os.listdir(month_path) if f.endswith('.nc')]

            # Loop through each data file, open dataset, and process daily data
            for data_file in data_files:
                file_path = os.path.join(month_path, data_file)
                data = xr.open_dataset(file_path)

                # Set spatial dimensions and CRS
                data.rio.set_spatial_dims(x_dim='lon', y_dim='lat', inplace=True)
                data.rio.write_crs('epsg:4326', inplace=True)

                # Iterate over each time slice (daily data)
                for time_index in data['time']:
                    daily_data_slice = data.sel(time=time_index)

                    # Clip data to Kenya boundary using Level 3 shapefile
                    try:
                        clipped_data_daily = daily_data_slice['sm_c4grass'].rio.clip(wards.geometry.apply(mapping), wards.crs, drop=True)

                        # Append data for each ward to the list for daily data
                        for ward in wards.itertuples():
                            ward_name = ward.NAME_3 
                            soil_moisture_value = clipped_data_daily.sel(lon=ward.geometry.centroid.x, lat=ward.geometry.centroid.y, method='nearest').item()
                            date = pd.to_datetime(str(time_index.values)).date()
                            ward_data[ward_name].append({
                                'Date': date,
                                'Soil_Moisture': soil_moisture_value
                            })
                    except Exception as e:
                        print(f"Error processing {data_file} {year}-{month_dir}: {e}")

    # Save each ward's data to separate Excel files
    output_dir = r'E:\Python\GeoPandas\WardOutput'  
    os.makedirs(output_dir, exist_ok=True) 

    for ward_name, data_list in ward_data.items():
        # Sanitize the ward name for the directory
        sanitized_ward_name = sanitize_filename(ward_name)
        ward_output_dir = os.path.join(output_dir, sanitized_ward_name)
        os.makedirs(ward_output_dir, exist_ok=True)  
        
        # Create a DataFrame for the ward
        ward_df = pd.DataFrame(data_list)
        # Define the path for the Excel file
        excel_path = os.path.join(ward_output_dir, f"{sanitized_ward_name}_Daily_Soil_Moisture.xlsx")
        # Write DataFrame to Excel
        ward_df.to_excel(excel_path, index=False)
        print(f"Daily soil moisture data for {ward_name} saved to {excel_path}")

# Parameters
base_dir = r'E:\Python\GeoPandas\Tamstat_data'
shapefile_path = r'E:\Python\GeoPandas\gadm41_KEN_shp\gadm41_KEN_3.shp'
start_year = 1983
end_year = 2024

# Create daily soil moisture data
create_daily_soil_moisture(base_dir, shapefile_path, start_year, end_year)
