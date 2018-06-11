# expenses.R
# prep the expenses data and push to Socrata
# Adam Scherling
# Written April 18, 2018. Updated June 11, 2018.

## Setup

# load required packages
if (!require("pacman")) install.packages("pacman")
pacman::p_load(dplyr, magrittr, tidyr, lubridate, data.table, RSocrata, readxl)

# set directories
# data = directory where the data are saved
# login = directory where Socrata login information is saved
#         (username.txt, password.txt - these should be plain text files 
#		   containing nothing but the username and password, respectively)
dir <- list(data="~/github/laBudget/proposed_budget/data/FY18-19/",
       login="~/github/laBudget/proposed_budget/scripts/")

# set the working directory
setwd(dir$data)

# url for the dataset
socrata_url <- "https://data.lacity.org/A-Prosperous-City/Open-Budget-Appropriations-Fiscal-Years-2010-2019/5242-pnmt"

# API endpoint for the dataset
socrata_endpoint <- "https://data.lacity.org/resource/ws4f-n5ax.json"

# filename of Excel spreadsheet
excel_file <- "Expenditures_Sec2 All Regular Depts and NonDepts_1819Proposed.xlsx"

# get Socrata username and password for upload
username <- readLines(paste0(dir$login, 'username.txt'))
password <- readLines(paste0(dir$login, 'password.txt'))

# get a timestamp
timestamp <- gsub(':','.',now())
timestamp <- gsub(' ','_',timestamp)

# prevent R from writing to scientific notation
options(scipen=999)


## Read In Data


# read in the new expenses data. section 2 only
new_expenses <- read_excel(excel_file) %>% data.frame

# remove rows with no 2018-2019 data
new_expenses %<>% filter(!is.na(X2018.19.Proposed))

# read in the existing data on Socrata
old_expenses <- read.socrata(socrata_url)

# filter out any 2019 data
old_expenses %<>% filter(fiscal_year!=2019)

# save a copy as a backup
write.csv(old_expenses, paste0('old_expenses_',timestamp,'.csv'), row.names=F)

colnames(new_expenses)
colnames(old_expenses)

# remove unnecessary columns from the new data
# (fund code, fund name, prior year appropriations/expenditures)
new_expenses <- new_expenses[,-c(7,8,13,14,15)]

# change the column names of the new data to match the old data
# missing columns: Program_Priority, Expense_Type
colnames(new_expenses) <- c("Dept_Code","Department_Name","SubDept_Code",
	"SubDepartment_Name","Prog_Code","Program_Name","Source_Fund_Code",
	"Source_Fund_Name","Account_Code","Account_Name","Appropriation")


## Get Program Priorities
# assign a category to each expenditure, e.g. A Well Run City, A Safe City,...
# an attempt is made to do this by matching the categories in the old dataset
# to new observations with the same department and program codes.
# unfortunately this doesn't work all that well

# for existing program names, get the program priority
priority <- old_expenses %>% select(Dept_Code, Prog_Code, Program_Priority)
priority <- priority[!duplicated(priority),]
priority <- na.omit(priority)

# remove duplicated Dept_Code, Prog_Code combinations. 
# somewhat undiscriminating, can be refined later
dd <- priority %>% select(Dept_Code, Prog_Code) %>% duplicated
priority <- priority[!dd,]

# merge in the program priority and expense type
new_expenses <- merge(new_expenses, priority, by=c("Dept_Code","Prog_Code"), all.x=T)

# examine the merge
sapply(colnames(new_expenses), function(j) sum(is.na(new_expenses[,j])))



### Miscellaneous data transformations


# add a fiscal year column
new_expenses$fiscal_year <- 2019

# add a blank expense_type column
new_expenses$expense_type <- NA

# arrange columns in the same order as the old expenses data
new_expenses %<>% select(colnames(old_expenses))

# convert appropriation column to character
new_expenses %<>% mutate(appropriation=as.character(appropriation))

# combine the old and new data
expenses <- rbind(new_expenses, old_expenses)

# sort according to fiscal year, department name, program name, account name
expenses %<>% arrange(desc(fiscal_year), department_name, program_name, account_name)


# write to csv
# write.csv(expenses, 'expenses.csv', row.names=F)

# upload the data to Socrata
write.socrata(dataframe = new_expenses,
              dataset_json_endpoint = socrata_endpoint,
              update_mode = "REPLACE",
              email = username,
              password = password)
