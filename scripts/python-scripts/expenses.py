#!/usr/bin/env python3
# expenses.py
# prep the expenses data and push to Socrata
# Adam Scherling April 18, 2018. Updated June 11, 2018
# Converted/Updated July 2021, Irene Tang


####################
## Setup
####################

# make sure to install these packages before running:
# pip install pandas
# pip install sodapy

import datetime
import pandas as pd
import numpy as np
import credentials
from sodapy import Socrata

# url for the dataset
socrata_url = 'https://data.lacity.org/A-Prosperous-City/Open-Budget-Appropriations-Fiscal-Years-2010-2019/5242-pnmt'

# API endpoint for the dataset
socrata_endpoint = 'https://data.lacity.org/resource/5242-pnmt.json'

# Identifier for the dataset
socrata_identifier = '5242-pnmt'

# set up Socrata client
client = Socrata('data.lacity.org', None)

# uncomment if you are going to log in / push to the data portal
# username = credentials.lahub_user
# password = credentials.lahub_pass
# apptoken = credentials.lahub_auth
# client = Socrata('data.lacity.org', apptoken, username=username, password=password)

# get the fiscal year being updated; default to the year after the current date
timestamp = datetime.datetime.now()
current_year = timestamp.year
new_fiscal_year = current_year + 1

####################
## Read in existing data
####################
filepath_prefix = '../../data/approved_budget/FY21-22/'

# read in the existing data on Socrata
old_expenses = pd.DataFrame.from_records(client.get(socrata_identifier, limit=99999999999999))

# save a copy as a local backup -- especially before pushing the output back to overwrite the existing data on Socrata
old_expenses.to_csv(
    f'{filepath_prefix}old_expenses_{timestamp}.csv', index=False)

# filter out any data from the fiscal year that's being updated (only keep the rows where fiscal_year!=new_fiscal_year)
old_expenses = old_expenses[old_expenses['fiscal_year']!=new_fiscal_year]

####################
## Read in new data
####################

# read in the new expenses data. section 2 only
csv_file = '../../data/approved_budget/FY21-22/Expenditures_Sec2_for_2122_Adopted.csv'
new_expenses = pd.read_csv(csv_file)

# keep only the desired columns
# assumes that the last column contains the data of interest (correct fiscal year, proposed/adopted as desired)
appropriation = new_expenses.columns[-1]  # e.g. '2021-22 Adopted'
new_expenses = new_expenses[['Dept Code', 'Dept Name', 'Org Level 5 Code', 'Org Level 5 Name', 'Prog Code', 'Prog Name', 'Source Fund Code', 'Source Fund Name', 'Account Code', 'Account Name', appropriation]]

# rename the columns of the new data to match the old data
# missing columns: Program_Priority, Expense_Type
new_expenses.columns = ['dept_code', 'department_name', 'subdept_code', 'subdepartment_name', 'prog_code', 'program_name', 'source_fund_code', 'source_fund_name', 'account_code', 'account_name', 'appropriation']

# remove rows with no appropriation data
new_expenses.dropna(how='all', subset=['appropriation'], inplace=True)



####################
## Get Program Priorities
# assign a category to each expenditure, e.g. A Well Run City, A Safe City
####################

## first, an attempt is made to do this by matching the categories in the old dataset to new observations with the same department and program codes. unfortunately this doesn't work all that well
priorities1 = old_expenses[['dept_code', 'prog_code', 'program_priority']]
# TODO unsure about the logic of this line? it was in the original .R so I kept it here commented-out
# priorities1 = priorities1.drop_duplicates(subset='program_priority', keep='first')
priorities1.dropna(inplace=True)

# remove duplicate Dept_Code, Prog_Code combinations
priorities1.drop_duplicates(subset=['dept_code', 'prog_code'], keep='first', inplace=True)

## merge in the program_priorities1
new_expenses = pd.merge(new_expenses, priorities1, on=['dept_code', 'prog_code'], how='left')
new_expenses.loc[new_expenses['program_priority']=='','program_priority']='Not Categorized'
new_expenses['program_priority'].fillna('Not Categorized', inplace = True)

new_expenses = new_expenses.astype({'prog_code': str})

## second, assign program priority using the descriptions dataset
program_priorities2_filename = '../../data/approved_budget/FY18-19/program_priorities.csv'
priorities2 = pd.read_csv(program_priorities2_filename)

priorities2.dropna(inplace=True)
priorities2 = priorities2[['Prog_Code', 'Program_Priority']]

priorities2.columns = [x.lower() for x in priorities2.columns]
priorities2 = priorities2.astype({'prog_code': str})


## merge in the program_priorities2 -- this will create two columns: program_priority_x, program_priority_y (one for each attempt)
new_expenses = pd.merge(new_expenses, priorities2, on='prog_code', how='left')

## consolidate the two estimates of priority, giving preference to the one from the descriptions dataset
new_expenses['program_priority'] = np.where(new_expenses.program_priority_y, new_expenses.program_priority_y, new_expenses.program_priority_y)

# fill the empty slots with 'Not Categorized'
new_expenses['program_priority'].fillna('Not Categorized', inplace = True)
new_expenses.loc[new_expenses['program_priority']=='','program_priority']='Not Categorized'

# delete columns program_priority_x, program_priority_y
new_expenses.drop(['program_priority_x', 'program_priority_y'], axis=1, inplace=True)



####################
### Miscellaneous data transformations
####################

# add a fiscal year column
new_expenses['fiscal_year'] = new_fiscal_year

# add a blank expense_type column. this is no longer provided
new_expenses['expense_type'] = None

# arrange columns in the same order as the old expenses data
new_expenses = new_expenses[old_expenses.columns]

# convert appropriation column to character
# new_expenses.assign(Appropriation=lambda x: str(x))

# combine the old and new data
expenses = pd.concat([new_expenses, old_expenses], axis=0)

# sort according to fiscal year, department name, program name, account name
expenses = expenses.astype({'fiscal_year': int})
expenses.sort_values(by=['fiscal_year'], ascending=False)
expenses.sort_values(by=['department_name', 'program_name', 'account_name'], ascending=True)

####################
## Save data
####################

# write to csv
expenses.to_csv(f'{filepath_prefix}new_expenses.csv')

# upload the data to Socrata
# client.replace(socrata_identifier, expenses)
