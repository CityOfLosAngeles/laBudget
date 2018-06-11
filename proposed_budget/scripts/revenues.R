# revenues.R
# Update the revenue data on Socrata. 
# It is presumed that the new data have already been converted from a pdf
# to a csv. Actually, two csv files: one for GF and SF revenues, another for
# available balances. The available balances will be added to revenues.
# Adam Scherling
# April 18, 2018. Updated June 11, 2018

## Setup

# load required packages
if (!require("pacman")) install.packages("pacman")
pacman::p_load(dplyr, magrittr, tidyr, lubridate, data.table, RSocrata, readxl)

# set directories
# data = directory where the data are saved
# login = directory where Socrata login information is saved
#         (username.txt, password.txt)
dir <- list(data="~/github/laBudget/proposed_budget/data/FY18-19/",
       login="~/github/laBudget/proposed_budget/scripts/")

# set the working directory
setwd(dir$data)

# url for the dataset
socrata_url <- "https://data.lacity.org/A-Prosperous-City/Open-Budget-Revenue-2010-2018/ih6g-qkwz"

# API endpoint for the dataset
socrata_endpoint <- "https://data.lacity.org/resource/y3a7-9ent.json"

# get Socrata username and password for upload
username <- readLines(paste0(dir$login, 'username.txt'))
password <- readLines(paste0(dir$login, 'password.txt'))

# get a timestamp
timestamp <- gsub(':','.',now())
timestamp <- gsub(' ','_',timestamp)

# prevent R from writing to scientific notation
options(scipen=999)


## Data

# read in the data on Socrata and save as a backup
old_revenues <- read.socrata(socrata_url)
write.csv(old_revenues, paste0("old_revenues_",timestamp,".csv"), row.names=F)

# filter out 2019 data
old_revenues %<>% filter(Fiscal.Year.Shorthand!=2019)

# read in the new data
new_revenues <- read.csv('new_revenues.csv', stringsAsFactors=F)
available_balances <- read.csv('available_balances.csv', stringsAsFactors=F)

# add the available balances to the revenues
new_revenues <- merge(new_revenues, available_balances, 
	by="Revenue.Source", all=T)
new_revenues$Available.Balance[is.na(new_revenues$Available.Balance)] <- 0
new_revenues %<>% mutate(Amount=as.numeric(Amount) + 
	as.numeric(Available.Balance))

# remove the available balances column
new_revenues %<>% select(-Available.Balance)

# merge with old revenues
revenues <- rbind(new_revenues, old_revenues)

# order by fiscal year, fund type, name
revenues %<>% arrange(desc(Fiscal.Year.Shorthand), Fund.Type, Revenue.Source)


# write to csv
# write.csv(revenues, 'revenues.csv', row.names=F)

# write to socrata
write.socrata(dataframe = revenues,
              dataset_json_endpoint = socrata_endpoint,
              update_mode = "REPLACE",
              email = username,
              password = password)
