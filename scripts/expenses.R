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
dir <- list(data="~/github/laBudget/data/approved_budget/FY18-19/",
       login="~/github/laBudget/scripts/")

# set the working directory
setwd(dir$data)

# url for the dataset
socrata_url <- "https://data.lacity.org/A-Prosperous-City/Open-Budget-Appropriations-Fiscal-Years-2010-2019/5242-pnmt"

# API endpoint for the dataset
# socrata_endpoint <- "https://data.lacity.org/resource/ws4f-n5ax.json"
socrata_endpoint <- "https://data.lacity.org/resource/5242-pnmt.json"

# filename of Excel spreadsheet
excel_file <- "Expenditures_Sec2 All Regular Depts and NonDepts_1819Adopted.xlsx"

# get Socrata username and password for upload
username <- readLines(paste0(dir$login, 'username.txt'))
password <- readLines(paste0(dir$login, 'password.txt'))

# get a timestamp
timestamp <- gsub(':','.',now())
timestamp <- gsub(' ','_',timestamp)

# prevent R from writing to scientific notation
options(scipen=999)

# get the fiscal year being updated
# default to the year after the current date
new_fiscal_year <- year(today()) + 1



## Back up existing data

# read in the existing data on Socrata
old_expenses <- read.socrata(socrata_url)

# save a copy as a backup
write.csv(old_expenses, paste0('old_expenses_',timestamp,'.csv'), row.names=F)

# filter out any data from the fiscal year that's being updated
old_expenses %<>% filter(Fiscal_Year!=new_fiscal_year)



## Read in new data

# read in the new expenses data. section 2 only
new_expenses <- read_excel(excel_file) %>% data.frame

# keep only the desired columns
# assumes that the last column contains the data of interest (correct fiscal year, proposed/adopted as desired)
new_expenses %<>% select(Dept.Code, Dept.Name, Org.Level.5.Code, Org.Level.5.Name, Prog.Code, Prog.Name,
	Source.Fund.Code, Source.Fund.Name, Account.Code, Account.Name, 
	colnames(new_expenses)[ncol(new_expenses)])

# change the column names of the new data to match the old data
# missing columns: Program_Priority, Expense_Type
colnames(new_expenses) <- c("Dept_Code","Department_Name","SubDept_Code",
	"SubDepartment_Name","Prog_Code","Program_Name","Source_Fund_Code",
	"Source_Fund_Name","Account_Code","Account_Name","Appropriation")

# remove rows with no appropriation data
new_expenses %<>% filter(!is.na(Appropriation))




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
# sapply(colnames(new_expenses), function(j) sum(is.na(new_expenses[,j])))



# alternatively: assign program priority using the descriptions dataset
priority2 <- read.csv('program_priorities.csv', stringsAsFactors=F) %>% select(Prog_Code, Program_Priority)
new_expenses <- merge(new_expenses, priority2, by="Prog_Code", all.x=T)

# merge the two estimates of priority, giving preference to the one from the descriptions dataset
new_expenses$Program_Priority <- ifelse(is.na(new_expenses$Program_Priority.y) | 
	new_expenses$Program_Priority.y=="", new_expenses$Program_Priority.x, new_expenses$Program_Priority.y)

new_expenses$Program_Priority[is.na(new_expenses$Program_Priority)] <- "Not Categorized"

# what portion of the appropriations have been assigned a program priority?
tapply(new_expenses$Appropriation, new_expenses$Program_Priority, sum) / sum(new_expenses$Appropriation)



### Miscellaneous data transformations


# add a fiscal year column.
new_expenses$Fiscal_Year <- new_fiscal_year

# add a blank expense_type column. this is no longer provided
new_expenses$Expense_Type <- NA

# arrange columns in the same order as the old expenses data
new_expenses %<>% select(colnames(old_expenses))

# convert appropriation column to character
new_expenses %<>% mutate(Appropriation=as.character(Appropriation))

# combine the old and new data
expenses <- rbind(new_expenses, old_expenses)

# sort according to fiscal year, department name, program name, account name
expenses %<>% arrange(desc(Fiscal_Year), Department_Name, Program_Name, Account_Name)


# write to csv
write.csv(expenses, 'expenses.csv', row.names=F)

# upload the data to Socrata
write.socrata(dataframe = expenses,
              dataset_json_endpoint = socrata_endpoint,
              update_mode = "REPLACE",
              email = username,
              password = password)
