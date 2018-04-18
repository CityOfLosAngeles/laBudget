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
write.csv(old_revenues, "old_revenues.csv", row.names=F)

# read in the new data
new_revenues <- read.csv('new_revenues.csv', stringsAsFactors=F)

# merge
revenues <- rbind(new_revenues, old_revenues)

# order by fiscal year, fund type, name
revenues %<>% arrange(desc(Fiscal.Year.Shorthand), Fund.Type, Revenue.Source)

# write to csv
write.csv(revenues, 'revenues.csv', row.names=F)
