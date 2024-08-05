
# Kenya soil moisture Analysis
# Overview
This project focuses on analyzing soil moisture data for Kenya, spanning the years 1983 to 2024. The data is sourced from TAMSAT and involves several key steps, including downloading, clipping, and visualizing soil moisture metric

# Objectives
Data Acquisition: writing a python script to download soil moisture data from TAMSAT data repository

Data Processing
Mapping/clipping the data to Kenya's geographical  boundaries as   our main region of focus
Calculate and visualize monthly, quarterly (three-month average), and Annual soil moisture averages.

Extracting the processed soil moisture data and export it to Excel in a time series format for further analysis
## Data 


Spatial domain	African continent, including Madagascar (N: 37.375°, S: -35.375°, W: -17.875°, E:51.375°)

Dimensions	292 pixels (latitude) by 278 pixels (longitude)

Spatial resolution	0.25° (approx. 25km)

Time-step	daily, pentadal, dekadal, monthly, seasonal

Data format	- 
NetCDF

Available variable -	sm_c4grass

Cost and Terms of use	- TAMSAT data are free to use and are released for operational, research and commercial use under the terms of the Creative Commons Attribution 4.0 International license (CC BY 4.0). To view a copy of this license, visit https://creativecommons.org/licenses/by/4.0/. 

Read more at : https://research.reading.ac.uk/tamsat/soil-moisture/

## Run Locally

Clone the project

```bash
  git clone https://github.com/kiptoorono/Kenya-soil-moisture-Analysis.git
```

Go to the project directory

```bash
  cd Kenya-soil-moisture-Analysis
```

Install dependencies

```bash
    pip install -r requirements.txt

```

Download Kenya Shape file level 3 from GADM

 link ->  https://gadm.org/download_country.html


Run the data downloading script

```bash
  WebCrawler.py
```


Run the quaterly plots script

```bash
  quaterly plots.py
```

run the data fetching script for the time series

```bash
  Time Series Matrix.py
```
** Note**
Make changes to directory paths in the scripts

## Documentation
[Kenya-soil-moisture-Analysis Docs](https://github.com/kiptoorono/Kenya-soil-moisture-Analysis/blob/main/Docs.pdf)
