# expenses.R
# prep the expenses data and push to Socrata
# Adam Scherling
# April 18, 2018

# load libraries
library(dplyr)
library(magrittr)
library(readxl)
library(RSocrata)

# set working directory
setwd('~/github/laBudget/proposed_budget/data/FY18-19')

# read in the new expenses data
sec2 <- read_excel("Expenditures_Sec2 All Regular Depts and NonDepts_1819Proposed.xlsx") %>% data.frame
# sec4 <- read_excel("Expenditures_Sec4 Library and Rec Parks_1819Proposed.xlsx") %>% data.frame

# merge into a single dataset
# new_expenses <- merge(sec2, sec4, all=T)
# rm(sec2, sec4)

new_expenses <- sec2

# remove rows with no 2018-2019 data
new_expenses %<>% filter(!is.na(X2018.19.Proposed))

# read in the existing data on Socrata
old_expenses <- read.socrata("https://data.lacity.org/resource/ws4f-n5ax.json")

# filter out any 2019 data
old_expenses %<>% filter(fiscal_year!=2019)

# save a copy as a backup
# write.csv(old_expenses, 'old_expenses.csv', row.names=F)

colnames(new_expenses)
colnames(old_expenses)

# remove unnecessary columns from the new data
# (fund code, fund name, prior year appropriations/expenditures)
new_expenses <- new_expenses[,-c(7,8,13,14,15)]

# change the column names of the new data to match the old data
# missing columns: Program_Priority, Expense_Type
colnames(new_expenses) <- c("dept_code","department_name","subdept_code",
	"subdepartment_name","prog_code","program_name","source_fund_code",
	"source_fund_name","account_code","account_name","appropriation")

# for existing program names, get the program priority
df <- old_expenses %>% select(dept_code, prog_code, program_priority)
df <- df[!duplicated(df),]
df <- na.omit(df)

# remove duplicated dept_code, prog_code combinations. 
# somewhat undiscriminating, can be refined later
dd <- df %>% select(dept_code, prog_code) %>% duplicated
df <- df[!dd,]

# merge in the program priority and expense type
new_expenses <- merge(new_expenses, df, by=c("dept_code","prog_code"), all.x=T)

# examine the merge
sapply(colnames(new_expenses), function(j) sum(is.na(new_expenses[,j])))

# add a fiscal year column
new_expenses$fiscal_year <- 2019

# add a blank expense_type column
new_expenses$expense_type <- NA

# arrange columns in the same order as the old expenses data
new_expenses %<>% select(colnames(old_expenses))

# prevent use of scientific notation when writing to csv
options(scipen=999)

# convert appropriation column to character
new_expenses %<>% mutate(appropriation=as.character(appropriation))

# combine the old and new data
expenses <- rbind(new_expenses, old_expenses)

# sort according to fiscal year, department name, program name, account name
expenses %<>% arrange(desc(fiscal_year), department_name, program_name, account_name)


# write to csv
write.csv(expenses, 'expenses.csv', row.names=F)

# # upload the data to Socrata
# user_password <- readLines("~/github/laBudget/proposed_budget/scripts/password.txt")

# write.socrata(dataframe = new_expenses,
#               dataset_json_endpoint = "https://data.lacity.org/resource/ws4f-n5ax.json",
#               update_mode = "REPLACE",
#               email = "adam.scherling@lacity.org",
#               password = user_password)
