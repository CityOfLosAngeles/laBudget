# revenue.py
# Update the revenue data on Socrata.
# It is presumed that the new data have already been converted from a pdf to a csv. Actually, two csv files: one for GF and SF revenues, another for available balances. The available balances will be added to revenues.
# Adam Scherling April 18, 2018. Updated June 11, 2018
# Converted/Updated July 2021, Calvin Chan


### This script will be able to creating new revenue entries in Socrata from the created CSV's via `parse_revenues.py`.

## SETUP

import datetime
import pandas as pd
import credentials
from sodapy import Socrata

# Instantiating variables
fy = '2021-2022'
fy_shorthand = 2022
filepath_prefix = '../../data/approved_budget/FY21-22/'

# API endpoint for the dataset
socrata_endpoint = "https://data.lacity.org/resource/ih6g-qkwz.json"
socrata_id = 'ih6g-qkwz'

# Get current timestamp
timestamp = str(datetime.datetime.now())

## EXTRACTING + CLEANING DATA


# set up Socrata client
# Don't need credentials to read in public data.
client = Socrata('data.lacity.org', None)

# uncomment if you are going to log in / push to the data portal
# username = credentials.lahub_user
# password = credentials.lahub_pass
# apptoken = credentials.lahub_auth
# client = Socrata('data.lacity.org', apptoken, username=username, password=password)

# read in the data on Socrata and save as backup
old_revenues = pd.DataFrame(client.get(socrata_id))
old_revenues.to_csv(f'{filepath_prefix}old_revenues_{timestamp}.csv')

# Filtering out current year
old_revenues = old_revenues[old_revenues['fiscal_year_2'] != 2022]

# Read in new data
new_revenues = pd.read_csv(
    '../../data/data/approved_budget/FY21-22/new_revenues.csv')
available_balances = pd.read_csv('../../available_balances.csv')

### Cleaning dataframes

# Remove percent columns
new_revenues.drop(columns=['Percent'], inplace=True)
available_balances.drop(columns=['Percent'], inplace=True)

# Remove rows without an available balance
available_balances = available_balances[available_balances['Available.Balance'] != 0]

# Cleaning new_revenues
new_revenues = new_revenues.merge(available_balances, how='outer', on='Revenue.Source')
new_revenues['Available.Balance'] = new_revenues['Available.Balance'].fillna(0)
new_revenues['Amount'] += new_revenues['Available.Balance']
new_revenues.drop(columns=['Available.Balance'], inplace=True)
new_revenues['Fiscal.Year.Shorthand'] = fy_shorthand
new_revenues['Fiscal.Year'] = fy

### Dropping rows that still have null values because this could mean these rows are just slightly misnamed in `Revenue.Source` w.r.t. the `Available Balances` table.
### The above is not necessarily true from year to year. Quality check of the data is still required.
new_revenues.dropna(axis=0, how='any', inplace=True)

# Renaming columns for `old_revenues`
old_revenues.rename(columns={
    'revenue_source': 'Revenue.Source',
    'amount': 'Amount',
    'fund_type': 'Fund.Type',
    'fiscal_year': 'Fiscal.Year',
    'fiscal_year_2': 'Fiscal.Year.Shorthand'
}, inplace=True)

### Dropping rows that still have null values from `old_revenues`. These entries are most likely continuously listed under similar names
### Quality check before this row would still be best practice.
old_revenues.dropna(axis=0, how='any', inplace=True)

## CREATING FINAL DATAFRAME AND UPLOADING TO SOCRATA

# Creating the `final_revenues` table and exporting it
final_revenues = pd.concat([new_revenues, old_revenues])
final_revenues.to_csv(f'{filepath_prefix}final_revenues.csv')

# Upload to Socrata here
