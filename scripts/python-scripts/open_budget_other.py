#!/usr/bin/env python3
# open_data_ther.py
# Chelsea Ursaner. Edited by Adam Scherling. 6/11/2018
# Converted/Updated July 2021, Irene Tang

####################
## Setup
####################

# make sure to install these packages before running:
# pip install pandas
# pip install sodapy

import datetime
import pandas as pd
import credentials
from sodapy import Socrata

# set up Socrata client
client = Socrata('data.lacity.org', None)

# uncomment if you are going to log in / push to the data portal
# username = credentials.lahub_user
# password = credentials.lahub_pass
# apptoken = credentials.lahub_auth
# client = Socrata('data.lacity.org', apptoken, username=username, password=password)

# csv sheet filenames
csv_filenames = {
    'gfrev': '../../data/approved_budget/FY21-22/General_Fund_Revenue_2122_Adopted.csv',
    'positions': '../../data/approved_budget/FY21-22/Positions_2122_Adopted.csv',
    'inc': '../../data/approved_budget/FY21-22/Budget_Requests_Detail_Sec2_2122_Adopted.csv',
    'pm': '../../data/approved_budget/FY21-22/Performance_Measures_2122_Adopted.csv',
}
filepath_prefix = '../../data/approved_budget/FY21-22/'

# # Socrata urls
# urls = {
#     'gfrev' : 'https://data.lacity.org/A-Prosperous-City/General-Fund-Revenue/qrkr-kfbh',
#     'positions' : 'https://data.lacity.org/A-Well-Run-City/Positions/46qe-t7np',
#     'inc' : 'https://data.lacity.org/A-Prosperous-City/General-City-Budget-Incremental-Changes/k4k6-bwwv',
#     'pm' : 'https://data.lacity.org/A-Prosperous-City/Performance-Measures/bywz-284j',
# }

# # Socrata endpoints
# endpoints = {
#     'gfrev' : 'https://data.lacity.org/resource/qrkr-kfbh.json',
#     'positions' : 'https://data.lacity.org/resource/46qe-t7np.json',
#     'inc' : 'https://data.lacity.org/resource/k4k6-bwwv.json',
#     'pm' : 'https://data.lacity.org/resource/bywz-284j.json',
# }

# Socrata identifiers
identifiers = {
    'gfrev': 'qrkr-kfbh',
    'positions': '46qe-t7np',
    'inc': 'k4k6-bwwv',
    'pm': 'bywz-284j'
}


timestamp = datetime.datetime.now()

####################
## General fund revenue
####################

# Read the previous dataset from Socrata and save a local copy
gfrev_existing = pd.DataFrame.from_records(client.get(identifiers.get('gfrev'), limit=99999999999999))
gfrev_existing.to_csv(f'{filepath_prefix}old_gfrev_{timestamp}.csv', index=False)

# Read the new file
gfrev_current = pd.read_csv(csv_filenames.get('gfrev'))

# Rename to match original
gfrev_current.rename(columns={
    'Dept Code': 'dept_code',
    'Dept Name': 'department_name',
    'Prog Code': 'program_code',
    'Prog Name': 'program_name',
    'Fund Code': 'fund_code',
    'Fund Name': 'fund_name',
    'Account Code': 'account_code',
    'Account Name': 'account_name',
    '2021-22 Adopted': 'revenue'
}, inplace=True)

# add a fiscal year column
gfrev_current['fiscal_year'] = '2021_22_adopted'

# filter out rows with no revenue
gfrev_current.dropna(how='all', subset=['revenue'], inplace=True)

# select only the relevant columns
gfrev_current = gfrev_current[gfrev_existing.columns]

# Make new dataset
gfrev_new = pd.concat([gfrev_existing, gfrev_current], axis=0)
gfrev_new.to_csv(f'{filepath_prefix}new_gfrev.csv', index=False)

# upload the data to Socrata
# client.replace('', gfrev_new)


###################
# Positions
###################

# Read the previous dataset from Socrata and save a local copy
positions_existing = pd.DataFrame.from_records(client.get(identifiers.get('positions'), limit=99999999999999))
positions_existing.to_csv(f'{filepath_prefix}old_positions_{timestamp}.csv', index=False)


# Read the new file
positions_current = pd.read_csv(csv_filenames.get('positions'))

# Rename to match original
positions_current.rename(columns={
    'Dept Code': 'department_code',
    'Dept Name': 'department_name',
    'Prog Code': 'program_code',
    'Prog Name': 'program_name',
    'Fund Code': 'fund_code',
    'Source Fund Code': 'source_fund_code',
    'Source Fund Name': 'source_fund_name',
    'Account Code': 'account_code',
    'Account Name': 'account_name',
    '2021-22 Adopted': 'positions'
}, inplace=True)

# add a budget column
positions_current['budget'] = '2021-2022 Adopted Budget'


# select only the relevant columns
positions_current = positions_current[positions_existing.columns]

# Make new dataset
positions_new = pd.concat([positions_existing, positions_current], axis=0)
positions_new.to_csv(f'{filepath_prefix}new_positions.csv', index=False)


# upload the data to Socrata
# client.replace('', positions_new)


###################
# Incremental changes
###################

# Read the previous dataset from Socrata and save a local copy
inc_existing = pd.DataFrame.from_records(client.get(identifiers.get('inc'), limit=99999999999999))
inc_existing.to_csv(f'{filepath_prefix}old_incremental_{timestamp}.csv', index=False)


# Read the new file
inc_current = pd.read_csv(csv_filenames.get('inc'))

# Rename to match original
inc_current.rename(columns={
    'Department Code': 'department_code',
    'Department Name': 'department_name',
    'Program Code': 'program_code',
    'Program Name': 'program_name',
    'Fund Code': 'fund_code',
    'Fund Name': 'fund_name',
    'Source Fund Code': 'source_fund_code',
    'Source Fund Name': 'source_fund_name',
    'Budget Request Description': 'budget_request_description',
    'Budget Request Category': 'budget_request_category',
    'Budget Object Code': 'account_code',
    'Audit Budget Object Name': 'account_name',
    'One Time/ On-going': 'one_time_ongoing',
    '2021-22 (Adopted) Incremental change from 2020-21 Adopted Budget': 'incremental_change'
}, inplace=True)


# add a fiscal year column
inc_current['budget'] = '2021-22 Adopted Budget Incremental Change from 2020-21 Adopted'

# select only the relevant columns
inc_current = inc_current[inc_existing.columns]

# Make new dataset
inc_new = pd.concat([inc_existing, inc_current], axis=0)
inc_new.to_csv(f'{filepath_prefix}new_incremental_changes.csv', index=False)


# upload the data to Socrata
# client.replace('', inc_new)


####################
## Performance Measures
####################

# Read the previous dataset from Socrata and save a local copy
pm_existing = pd.DataFrame.from_records(client.get(identifiers.get('pm'), limit=99999999999999))
pm_existing.to_csv(f'{filepath_prefix}old_performance_{timestamp}.csv', index=False)


# Read the new file
pm_current = pd.read_csv(csv_filenames.get('pm'))

# Rename to match original
pm_current.rename(columns={
    'Dept Code': 'department_code',
    'Department Name': 'department_name',
    'Org Level 5 Code': 'subdept_code',
    'Org Level 5 Name': 'subdept_name',
    'Prog Code': 'program_code',
    'Program Name': 'program_name',
    'PM Code': 'performance_measure_code',
    'Performance Measure Name': 'performance_measure_name',
    'Unit/Value': 'unit',
    '2021-22 Adopted': 'performance_measure_amount'
}, inplace=True)


# add a fiscal year column
pm_current['budget'] = '2021-22 Adopted'

# select only the relevant columns
pm_current = pm_current[pm_existing.columns]


# Make new dataset
pm_new = pd.concat([pm_existing, pm_current], axis=0)
pm_new.to_csv(f'{filepath_prefix}new_performance_measures.csv', index=False)


# upload the data to Socrata
# client.replace('', inc_new)
