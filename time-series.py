import os
import geopandas as gpd
import xarray as xr
import rioxarray
import pandas as pd
from shapely.geometry import mapping

# Function to process all years and create a time series of soil moisture data for each ward
def create_soil_moisture_time_series(base_dir, shapefile_path, start_year, end_year, excel_path):
    # Load Shapefile
    wards = gpd.read_file(shapefile_path)
    
    # Initialize dictionary to store data
    time_series_data = {ward: [] for ward in wards['NAME_3']}  # Assuming 'NAME_3' is the ward name column
    
    # Define three-month periods
    three_month_groups = {
        'Jan-Mar': ['01', '02', '03'],
        'Apr-Jun': ['04', '05', '06'],
        'Jul-Sep': ['07', '08', '09'],
        'Oct-Dec': ['10', '11', '12']
    }
    
    # Iterate through each year
    for year in range(start_year, end_year + 1):
        year_dir = os.path.join(base_dir, str(year))
        if not os.path.isdir(year_dir):
            continue

        print(f"Processing year: {year}")

        # Initialize list to store monthly averages for the selected year
        monthly_averages_selected_year = []

        # Iterate over each month directory within the selected year
        for month_dir in sorted(os.listdir(year_dir)):
            month_path = os.path.join(year_dir, month_dir)

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
                clipped_data_monthly = mean_sm_c4grass_monthly.rio.clip(wards.geometry.apply(mapping), wards.crs, drop=True)

                # Append monthly average to list for the selected year
                monthly_averages_selected_year.append((month_dir, clipped_data_monthly))
            except Exception as e:
                print(f"Error processing {month_dir} {year}: {e}")

        # Calculate average for each three-month period and append to the time series data
        for period, months in three_month_groups.items():
            period_data = [data for month, data in monthly_averages_selected_year if month in months]

            if period_data:
                period_average = xr.concat(period_data, dim='time').mean(dim='time')

                # Set spatial dimensions and CRS for the three-month average
                period_average.rio.set_spatial_dims(x_dim='lon', y_dim='lat', inplace=True)
                period_average.rio.write_crs('epsg:4326', inplace=True)

                # Clip data to Kenya boundary for the three-month average
                clipped_data_period = period_average.rio.clip(wards.geometry.apply(mapping), wards.crs, drop=True)

                # Append data for each ward to the time series data
                for ward in wards.itertuples():
                    ward_name = ward.NAME_3  # Assuming 'NAME_3' is the ward name column
                    soil_moisture_value = clipped_data_period.sel(lon=ward.geometry.centroid.x, lat=ward.geometry.centroid.y, method='nearest').item()
                    time_series_data[ward_name].append({
                        'Year': year,
                        'Period': period,
                        'Soil_Moisture': soil_moisture_value
                    })
            else:
                print(f"No data available for period {period} {year}")

    # Create DataFrame to store the time series data
    all_data = []
    for ward_name, values in time_series_data.items():
        for entry in values:
            entry['Ward'] = ward_name
            all_data.append(entry)

    time_series_df = pd.DataFrame(all_data)

    # Pivot the DataFrame to have wards as columns and time periods as rows
    pivot_df = time_series_df.pivot_table(index=['Year', 'Period'], columns='Ward', values='Soil_Moisture')

    # Save DataFrame to Excel
    pivot_df.to_excel(excel_path)
    print(f"Time series data saved to {excel_path}")

# Parameters
base_dir = r'E:\Python\GeoPandas\Tamstat_data'
shapefile_path = r'E:\Python\GeoPandas\gadm41_KEN_shp\gadm41_KEN_3.shp'
start_year = 1983
end_year = 2024
excel_path = "Kenya_Average_Soil_Moisture_Time_Series_1983_2024.xlsx"

# Create time series data
create_soil_moisture_time_series(base_dir, shapefile_path, start_year, end_year, excel_path)
