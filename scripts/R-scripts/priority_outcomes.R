# priority_outcomes.R
# filter the priority outcomes from the program description spreadsheet
# Adam Scherling
# April 18, 2018

library(readxl)
library(dplyr)

setwd('~/github/laBudget/proposed_budget/data/FY18-19')

programs <- read_excel('QRY Program Description Text_1819Proposed.xlsx') %>% data.frame

descriptions <- programs[,3]

priority_outcomes <- vector(length=nrow(programs))
for (i in 1:nrow(programs)) {
	desc <- descriptions[i]
	tmp <- strsplit(desc, '\n')[[1]]
	if (substr(tmp,1,8)=="Priority") {
		priority_outcomes[i] <- substr(tmp, 19, nchar(tmp))
	} else {
		priority_outcomes[i] <- NA
	}
}
