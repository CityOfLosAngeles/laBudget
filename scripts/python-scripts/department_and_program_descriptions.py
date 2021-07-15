# department_and_program_descriptions.py
# update the department and program descriptions on Socrata
# written by Adam Scherling, June 12, 2018
# edited/updated Irene Tang, July 2021

###################
# Setup
###################

# make sure to install these packages before running:
# pip install pandas
# pip install sodapy

import datetime
import pandas as pd
import numpy as np
from sodapy import Socrata

# url for the dataset
socrata_url = 'https://data.lacity.org/A-Well-Run-City/LA-City-Department-and-Program-Descriptions/cd49-p4un'

# Identifier for the dataset
socrata_identifier = 'cd49-p4un'

# API endpoint for the dataset
socrata_endpoint = 'https://data.lacity.org/resource/cd49-p4un.json'

# filenames
filepath_prefix = '../../data/approved_budget/FY21-22/'
filenames = {
    'departments': '../../data/approved_budget/FY21-22/QRY_Department_Name_Text_2122_Adopted.csv',
    'programs': '../../data/approved_budget/FY21-22/QRY_Program_Description_Text_2122_Adopted.csv',
}

# set up Socrata client
client = Socrata('data.lacity.org', None)

# uncomment if you are going to log in / push to the data portal
# with open('credentials.lahub_auth') as a:
#     apptoken = a.readline()
# with open('credentials.lahub_user') as u:
#     username = u.readline().strip()
# with open('credentials.lahub_pass') as p:
#     password = p.readline()
# client = Socrata('data.lacity.org', apptoken, username=username, password=password)

timestamp = datetime.datetime.now()

####################
## Read in existing data
####################

# Read the previous dataset from Socrata and save a local copy
old_descriptions = pd.DataFrame.from_records(client.get(socrata_identifier, limit=99999999999999))
old_descriptions.to_csv(f'{filepath_prefix}old_descriptions_{timestamp}.csv', index=False)

####################
## Read in new program data
####################

# read in the new programs
new_programs = pd.read_csv(filenames.get('programs'))

# rename the columns to match the Socrata dataset
new_programs.columns = ['program_number', 'entity_name', 'description']

# drop the row if the whole row is empty
new_programs.dropna(how='all', inplace=True)


# add an entity type column
new_programs['entity_type'] = 'Program'


####################
## Handle priority outcomes
####################

# many of the programs have a priority outcome in the description. these should be removed from the descriptions, but saved in a separate file that can be used to label the priority of programs in the expenses data

# first, convert any NA descriptions to blank strings
new_programs['description'] = new_programs['description'].fillna('')

# now loop over all the descriptions and separate out the program priorities
program_priority = []
new_desc = ''
for i, old_desc in enumerate(new_programs.description):
    new_desc = ''
    old_desc = old_desc.strip()
    # if a program priority is given
    if ('Priority Outcome:' in old_desc[:18]) or ('Priority Outcomes:' in old_desc[:18]):
        end_priority_name = old_desc.find('\r')
        begin_priority_name = old_desc.find(':') + 1

        priority = old_desc[begin_priority_name:end_priority_name].strip()
        new_desc = old_desc[end_priority_name:].strip()
    # else if not given
    else:
        priority = 'NA'
    program_priority.append(priority)
    new_programs.description[i] = new_desc

# convert program priorities to language used in the expenses data
for i, old_priority in enumerate(program_priority):
    new_priority = ''
    if('livable' in old_priority):
        new_priority = 'A Livable and Sustainable City'
    elif('best' in old_priority):
        new_priority = 'A Well Run City'
    elif('jobs' in old_priority):
        new_priority = 'A Prosperous City'
    elif('safe' in old_priority):
        new_priority = 'A Safe City'
    program_priority[i] = new_priority

# create a data frame of the program priorities and write to csv
program_priority_df = pd.DataFrame({
    'program_number' : new_programs.program_number.astype('Int64'),
    'program_name' : new_programs.entity_name,
    'program_priority' : program_priority,
})
program_priority_df.to_csv(f'{filepath_prefix}new_program_priorities.csv', index=False)

# remove the program number from the new_programs data frame - no longer needed
new_programs.drop(columns=['program_number'], inplace=True)

####################
## Read in the new department data 
####################

# read in the new department descriptions (don't want the first column)
new_departments = pd.read_csv(filenames.get('departments')).iloc[:, 1:]

# drop the row if the whole row is empty
new_departments.dropna(how='all', inplace=True)


# add an entity type column
new_departments['entity_type'] = 'Department'

# rename the columns to match the Socrata dataset
new_departments.columns = new_programs.columns

# combine the two files
new_descriptions = pd.concat([new_departments, new_programs], axis=0)

# rearrange the columns
new_descriptions = new_descriptions[old_descriptions.columns]


####################
## Save data
####################

# write to csv
new_descriptions.to_csv(f'{filepath_prefix}new_descriptions.csv', index=False)

# upload the data to Socrata
# client.replace('', expenses)



# reformat for uploading as annotations on the open budget site
new_descriptions['entity_type'] = new_descriptions['entity_type'].replace(['Program', 'Department'], ['program_name', 'department_name'])
new_descriptions.columns = ['column', 'entity', 'text']

# write to csv
new_descriptions.to_csv(f'{filepath_prefix}new_annotations.csv', index=False)
