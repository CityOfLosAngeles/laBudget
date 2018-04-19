# revenues.R
# update the revenue data on Socrata. This presumes that the new data are already available as a csv
# Adam Scherling
# April 18, 2018

library(RSocrata)
library(dplyr)
library(magrittr)

# set the working directory
setwd('~/github/laBudget/proposed_budget/data/FY18-19')

# read in the old data and save as a backup
old_revenues <- read.socrata("https://data.lacity.org/A-Prosperous-City/Open-Budget-Revenue-2010-2018/ih6g-qkwz/data")
# write.csv(old_revenues, "old_revenues.csv", row.names=F)
# old_revenues %<>% filter(Fiscal.Year.Shorthand!=2019)

# read in the new data
new_revenues <- read.csv('new_revenues.csv', stringsAsFactors=F)
available_balances <- read.csv('available_balances.csv', stringsAsFactors=F)

# add the available balances to the revenues
new_revenues <- merge(new_revenues, available_balances, by="Revenue.Source", all=T)
new_revenues$Available.Balance[is.na(new_revenues$Available.Balance)] <- 0
new_revenues %<>% mutate(Amount=as.numeric(Amount) + as.numeric(Available.Balance))

# remove the available balances column
new_revenues %<>% select(-Available.Balance)

# merge with old revenues
revenues <- rbind(new_revenues, old_revenues)

# order by fiscal year, fund type, name
revenues %<>% arrange(desc(Fiscal.Year.Shorthand), Fund.Type, Revenue.Source)

# prevent R from writing to scientific notation
options(scipen=999)

# write to csv
write.csv(revenues, 'revenues.csv', row.names=F)
