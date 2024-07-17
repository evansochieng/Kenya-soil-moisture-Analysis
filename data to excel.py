import pandas as pd

# Initialize a list to store the final DataFrame
all_data = []

# Loop through each year and calculate quarterly averages
for year_path in year_paths:
    selected_year = os.path.basename(year_path)
    
    # Initialize list to store monthly averages for the selected year
    monthly_averages_selected_year = []

    # Iterate over each month directory within the selected year
    for month_dir in os.listdir(year_path):
        month_path = os.path.join(year_path, month_dir)
        
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

    # Calculate average for each three-month period and add to DataFrame
    for period, months in three_month_groups.items():
        period_data = [data for month, data in monthly_averages_selected_year if month in months]

        if period_data:
            period_average = xr.concat(period_data, dim='time').mean(dim='time')

            # Extract data values and create a DataFrame
            period_df = period_average.to_dataframe().reset_index()
            period_df['Year'] = selected_year
            period_df['Period'] = period
            all_data.append(period_df)

# Concatenate all data into a single DataFrame
final_df = pd.concat(all_data)

# Save to Excel file
excel_path = 'Kenya_Soil_Moisture_Quarterly_Avrg.xlsx'
final_df.to_excel(excel_path, index=False)

print(f"Data saved to {excel_path}")
