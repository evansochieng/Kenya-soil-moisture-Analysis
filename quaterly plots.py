import os
import geopandas as gpd
import xarray as xr
import rioxarray
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from shapely.geometry import mapping
from matplotlib.colors import LinearSegmentedColormap

# Custom colormap - Black, Red, Green -
colors = [(0.0, 0.0, 0.0), (1.0, 0.0, 0.0), (0.0, 1.0, 0.0)]  
custom_cmap = LinearSegmentedColormap.from_list('custom_cmap', colors, N=256)

# parent Directory
base_dir = r"E:\Python\GeoPandas\Tamstat_data"

# Load Kenya shapefile
kenya = gpd.read_file(r'E:\Python\GeoPandas\gadm41_KEN_shp\gadm41_KEN_3.shp')
# Create a dictionary to store paths for each year
year_paths = {}
for year_dir in os.listdir(base_dir):
    year_path = os.path.join(base_dir, year_dir)
    if os.path.isdir(year_path):
        year_paths[year_dir] = year_path

# PDF file to save plots
pdf_path = "Kenya_Average_Soil_Moisture_Quarterly_All_Years.pdf"
with PdfPages(pdf_path) as pdf:
    for selected_year, selected_year_path in year_paths.items():
        print(f"Processing year: {selected_year}")

        # Initialize list to store monthly averages for the selected year
        monthly_averages_selected_year = []
        for month_dir in sorted(os.listdir(selected_year_path)):
            month_path = os.path.join(selected_year_path, month_dir)
            if not os.path.isdir(month_path):
                continue
            # Create a list of nc file paths within that month
            data_files = [f for f in os.listdir(month_path) if f.endswith('.nc')]

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

        # Calculate average for each three-month period and plot
        for period, months in three_month_groups.items():
            period_data = [data for month, data in monthly_averages_selected_year if month in months]

            if period_data:
                period_average = xr.concat(period_data, dim='time').mean(dim='time')

                # Set spatial dimensions and CRS for the three-month average
                period_average.rio.set_spatial_dims(x_dim='lon', y_dim='lat', inplace=True)
                period_average.rio.write_crs('epsg:4326', inplace=True)

                # Clip data to Kenya boundary for the three-month average
                clipped_data_period = period_average.rio.clip(kenya.geometry.apply(mapping), kenya.crs, drop=True)

                # Plotting three-month average
                fig, ax = plt.subplots(1, 1, figsize=(10, 10))
                kenya.plot(ax=ax, facecolor='none', edgecolor='black', linewidth=0.5)
                clipped_data_period.plot(ax=ax, zorder=-1, cmap=custom_cmap, cbar_kwargs={'label': 'Soil Moisture (sm_c4grass)'})

                plt.title(f'Average Soil Moisture ({period} {selected_year})', fontsize=16)
                ax.set_xlabel('Longitude [degrees East]', fontsize=12)
                ax.set_ylabel('Latitude [degrees North]', fontsize=12)
                ax.set_xticks(range(34, 42, 2))
                ax.set_yticks(range(-4, 6, 2))

                pdf.savefig(fig, bbox_inches='tight')
                plt.close(fig)
            else:
                print(f"No data available for period {period} {selected_year}")

print(f"Plots saved to {pdf_path}")
