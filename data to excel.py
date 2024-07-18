import os
import geopandas as gpd
import xarray as xr
import rioxarray
import pandas as pd
from shapely.geometry import mapping

# Function to process a single year and write the results to an Excel file
def process_single_year(selected_year, base_dir, shapefile_path, excel_path):
    # Loading Shapefile
    kenya = gpd.read_file(shapefile_path)
    
    # Directory for the selected year
    selected_year_path = os.path.join(base_dir, selected_year)

    if not os.path.isdir(selected_year_path):
        print(f"Directory for the selected year {selected_year} does not exist.")
        return

    print(f"Processing year: {selected_year}")

    # Initialize list to store monthly averages for the selected year
    monthly_averages_selected_year = []

    # Iterate over each month directory within the selected year
    for month_dir in sorted(os.listdir(selected_year_path)):
        month_path = os.path.join(selected_year_path, month_dir)

        # Check if it's a directory
        if not os.path.isdir(month_path):
            continue  # Skip if it's not a directory

        # Create a list of nc file paths within that month
        data_files = [f for f in os.listdir(month_path) if f.endswith('.nc')]

        # Initialize an empty list to store datasets
        datasets = []

        # Loop through each data file, open dataset, and append to datasets list
        for data_file in data_files:
            file_path = os.path.join(month_path, data_file)
            data = xr.open_dataset(file_path)
            datasets.append(data)

        # Concatenate datasets along time dimension
        combined_data = xr.concat(datasets, dim='time')

        # Calculate mean of 'sm_c4grass' along the time dimension (monthly average)
        mean_sm_c4grass_monthly = combined_data['sm_c4grass'].mean(dim='time')

        # Set spatial dimensions and CRS
        mean_sm_c4grass_monthly.rio.set_spatial_dims(x_dim='lon', y_dim='lat', inplace=True)
        mean_sm_c4grass_monthly.rio.write_crs('epsg:4326', inplace=True)

        # Clip data to Kenya boundary using Level 3 shapefile
        try:
            clipped_data_monthly = mean_sm_c4grass_monthly.rio.clip(kenya.geometry.apply(mapping), kenya.crs, drop=True)

            # Append monthly average to list for the selected year
            monthly_averages_selected_year.append((month_dir, clipped_data_monthly))
        except Exception as e:
            print(f"Error processing {month_dir} {selected_year}: {e}")

    # Group the monthly data into three-month periods and calculate the average
    three_month_groups = {
        'Jan-Mar': ['01', '02', '03'],
        'Apr-Jun': ['04', '05', '06'],
        'Jul-Sep': ['07', '08', '09'],
        'Oct-Dec': ['10', '11', '12']
    }

    # Initialize Excel writer
    with pd.ExcelWriter(excel_path, engine='openpyxl') as writer:
        # Calculate average for each three-month period and save to Excel
        for period, months in three_month_groups.items():
            period_data = [data for month, data in monthly_averages_selected_year if month in months]

            if period_data:
                period_average = xr.concat(period_data, dim='time').mean(dim='time')

                # Set spatial dimensions and CRS for the three-month average
                period_average.rio.set_spatial_dims(x_dim='lon', y_dim='lat', inplace=True)
                period_average.rio.write_crs('epsg:4326', inplace=True)

                # Clip data to Kenya boundary for the three-month average
                clipped_data_period = period_average.rio.clip(kenya.geometry.apply(mapping), kenya.crs, drop=True)

                # Create a DataFrame to store soil moisture data along with polygon shapes
                soil_moisture_df = kenya.copy()
                soil_moisture_df['Soil_Moisture'] = [
                    clipped_data_period.sel(lon=geometry.centroid.x, lat=geometry.centroid.y, method='nearest').item()
                    for geometry in soil_moisture_df.geometry
                ]

                # Save DataFrame to Excel
                sheet_name = f"{selected_year}_{period}"
                soil_moisture_df.to_excel(writer, sheet_name=sheet_name, index=False)
            else:
                print(f"No data available for period {period} {selected_year}")

    print(f"Data saved to {excel_path}")

# Parameters
base_dir = r'E:\Python\GeoPandas\Tamstat_data'
shapefile_path = r'E:\Python\GeoPandas\gadm41_KEN_shp\gadm41_KEN_3.shp'

# Prompt the user to enter the year they want to process
selected_year = input("Enter the year you want to process: ")

# Output Excel file path
excel_path = f"Kenya_Average_Soil_Moisture_{selected_year}.xlsx"

# Process the selected year
process_single_year(selected_year, base_dir, shapefile_path, excel_path)
