# Kenya-soil-moisture-Analysis
This repository contains a Python script for processing and visualizing soil moisture data in Kenya from (19833 to date).
The script processes .nc files to compute monthly and annual average soil moisture levels, clipped to the administrative boundaries of Kenya (level 3). The results are saved as PDF plots.
Monthly average is computed since the soil moisture(sm_c4grass) is measured in 3 decads(measured in a period of 10 days) thus we need to calculate the mean of all three decads to perform monthly visualisation
The code prompts user to input year to perform analysis since the data set is huge and we need to utilise computing power by only excecuting for single years that are needed.
***NOTE*******
since the data set is huge:
Execute the web crawler script to fetch data from Tamsat to your local machine
