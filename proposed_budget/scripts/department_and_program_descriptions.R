# department_and_program_descriptions.R
# update the department and program descriptions on Socrata
# written by Adam Scherling, June 12, 2018



## Setup #############

# load required packages
if (!require("pacman")) install.packages("pacman")
pacman::p_load(dplyr, magrittr, tidyr, lubridate, data.table, RSocrata, readxl)

# set directories
# data = directory where the data are saved
# login = directory where Socrata login information is saved
#         (username.txt, password.txt - these should be plain text files 
#		   with the first line containing nothing but the username or 
#          password, respectively, and the second line blank)
dir <- list(data="~/github/laBudget/proposed_budget/data/FY18-19/",
       login="~/github/laBudget/proposed_budget/scripts/")

# set the working directory
setwd(dir$data)

# url for the dataset
socrata_url <- "https://data.lacity.org/A-Well-Run-City/LA-City-Department-and-Program-Descriptions/cd49-p4un"

# API endpoint for the dataset
socrata_endpoint <- "https://data.lacity.org/resource/cd49-p4un.json"

# filenames
filenames <- list()
filenames$departments <- "QRY Department Description Text_1819Proposed.xlsx"
filenames$programs <- "QRY Program Description Text_1819Proposed.xlsx"

# get Socrata username and password for upload
username <- readLines(paste0(dir$login, 'username.txt'))
password <- readLines(paste0(dir$login, 'password.txt'))

# get a timestamp
timestamp <- gsub(':','.',now())
timestamp <- gsub(' ','_',timestamp)

# prevent R from writing to scientific notation
options(scipen=999)





## Back up the existing data ###############

# read in the existing data on Socrata
old_descriptions <- read.socrata(socrata_url)

# save a copy as a backup
write.csv(old_descriptions, paste0('old_descriptions_',timestamp,'.csv'), 
	row.names=F)






## Read in the new program descriptions ##############

new_programs <- read_excel(filenames$programs)

# rename the columns to match the Socrata dataset
colnames(new_programs) <- c("Program.Number","Entity.Name","Description")

# add an entity type column
new_programs$Entity.Type <- "Program"

# many of the programs have a priority outcome in the description.
# these should be removed from the descriptions, but saved in a separate file
# that can be used to label the priority of programs in the expenses data

# first, convert any NA descriptions to blank strings
new_programs$Description[is.na(new_programs$Description)] <- ''

# now loop over all the descriptions and separate out the program priorities
program_priority <- vector(length=nrow(new_programs))
for (i in 1:nrow(new_programs)) {
	desc.tmp <- new_programs$Description[i]
	# if there is a program priority, separate it and save it
	if (substr(desc.tmp,1,17)=="Priority Outcome:") {
		pos <- regexpr('\r',desc.tmp)
		priority <- substr(desc.tmp, 19, pos-1)
		new_desc <- substr(desc.tmp, pos, nchar(desc.tmp))
		new_desc <- gsub('\r','', new_desc)
		new_desc <- gsub('\n','', new_desc)
	} else if (substr(desc.tmp,1,18)=="Priority Outcomes:") {
		pos <- regexpr('\r',desc.tmp)
		priority <- substr(desc.tmp, 20, pos-1)
		new_desc <- substr(desc.tmp, pos, nchar(desc.tmp))
		new_desc <- gsub('\r','', new_desc)
		new_desc <- gsub('\n','', new_desc)
	} else {
		# if there isn't a program priority, mark priority as NA
		# but still clean up the description, getting rid of \r and \n chars
		priority <- 'NA'
		new_desc <- desc.tmp
		new_desc <- gsub('\r','', new_desc)
		new_desc <- gsub('\n','', new_desc)
	}
	program_priority[i] <- priority
	new_programs$Description[i] <- new_desc
}

# convert program priorities to language used in the expenses data
for (i in 1:length(program_priority)) {
	priority.tmp <- program_priority[i]
	if (regexpr("livable", priority.tmp)!=-1) {
		out <- "A Livable and Sustainable City"
	} else if (regexpr("best", priority.tmp)!=-1) {
		out <- "A Well Run City"
	} else if (regexpr("jobs", priority.tmp)!=-1) {
		out <- "A Prosperous City"
	} else if (regexpr("safe", priority.tmp)!=-1) {
		out <- "A Safe City"
	} else {
		out <- ""
	}
	program_priority[i] <- out
}

# create a data frame of the program priorities and write to csv
program_priority.df <- data.frame(Prog_Code=new_programs$Program.Number,
	Program_Name=new_programs$Entity.Name, Program_Priority=program_priority)
write.csv(program_priority.df, 'program_priorities.csv', row.names=F)


# remove the program number from the new_programs data frame - no longer needed
new_programs %<>% select(-Program.Number)






## Read in the new department descriptions ##############

new_departments <- read_excel(filenames$departments)[,2:3]

# rename the columns to match the Socrata dataset
colnames(new_departments) <- c("Entity.Name","Description")

# add an entity type column
new_departments$Entity.Type <- "Department"

# combine the two files
new_descriptions <- rbind(new_programs, new_departments)

# rearrange the columns
new_descriptions %<>% select(colnames(old_descriptions))




## Write the new descriptions to csv to take a look ################
# (ok to delete it afterwards)

write.csv(new_descriptions, paste0('new_descriptions_',timestamp,'.csv'), row.names=F)



## Write the new descriptions to Socrata ################

new_descriptions %<>% data.frame

write.socrata(dataframe = new_descriptions,
              dataset_json_endpoint = socrata_endpoint,
              update_mode = "REPLACE",
              email = username,
              password = password)
