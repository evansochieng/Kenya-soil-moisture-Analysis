# Kenya-soil-moisture-Analysis
This repository contains a Python script for processing and visualizing soil moisture data in Kenya from (19833 to date).
                    ** Objectives
OVisualise the data  to assist relevant sectors in monitoring land surface and identify areas where Matured crops are likely to be undergoing water Stress. and provide valuable insights in identifying conditions that can lead to poor crop growth or even crop failure.

                ** Requirements**
Python 3.x  Libraries: xarray, rasterio, matplotlib, pandas

                ** Overview ***
The script processes .nc files to compute monthly and annual average soil moisture levels, clipps it to the administrative boundaries of Kenya (level 3). The results are then saved as PDF plots for easier access.
Monthly average is computed since the soil moisture(sm_c4grass) is measured in 3 decads(measured in a period of 10 days) thus we need to calculate the mean of all three decads to perform monthly aggregation and plotting.
It prompts user to input year to perform aggregation & plotting for that specific Year

                ** Running the Script**
1. Ensure you have the required libraries installed.
2. Download and organize your NetCDF data files with a structure where each year has its own directory.(I got you :), WebCrawler.py will do that for you )
3. Update the script (if needed) to point to the location of your data directory.
4. Run the script using python script_name.py.
5. The script will prompt you to select a year from available options.
6. Upon completion, a PDF file (Kenya_Average_Soil_Moisture_{selected_year}.pdf) will be generated containing the plots for the chosen year.

                     ***NOTE*******
1. Execute the Webcrawler.py Script first to fetch the data from Tamsat
2. since the data set is huge, I implemented lazy loading, files paths are stored to a list and a single year path that a user selects is processed. This utilises time & computational resouces compared to the approach of loading the entire dataset.
3. The pdf files are plots of few years that I had already processed.

                    ****Data Source***
The data was obtained from Tamsat (Tropical Applications of Meteorology using SATellite data and ground-based observations.)
link to their web page: https://www.tamsat.org.uk

                    ** Challenge :) **

1. Refactor code - The code includes repetitive sections for plotting monthly and annual average soil moisture. Can you refactor it into a reusable function to improve maintainability and reduce code duplication?

2. Explore Faster Loading and Processing - For very large datasets, loading and processing everything at once might be inefficient. Can you explore techniques like chunking to potentially improve performance?

3. To contribute your changes, submit a pull request 

                    ** code update**

Added a cell  that computes quaterly average of "sm_c4grass" and plaots the average of  each quater of years from 1983 and plots them to a single pdf