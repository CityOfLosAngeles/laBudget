# Background
Every year on April 20th, the mayor releases a proposed budget. After typically a few modifications, the budget is then adopted by City Council in June. While this has been the process in Los Angeles for some time, we only recently started putting the proposed and adopted budgets and related datasets onto the Open Data Portal each year as part of Mayor Garcetti’s open data initiative. 

Again, the data needs to be updated twice a year - when the proposed budget is released and when the adopted budget is released - so it was fine in the past to do this pretty manually using the excel exports we get from the City Administrative Office. But for the sustainability of the open data program, and to get the data to Angelenos quickly, it was time to get more programmatic about it. 

For this project, we started by picking one dataset - General Fund Revenue. Our task was to write a script that merged the new export of data into the current dataset (easier said than done without a unique identifier), and that we could rerun with minimal changes for future budget releases. We collaborated using R to complete the project and learned from each other along the way to make a programmatic update method for more datasets like Budget Expenses, Incremental Changes, and Performance Measures as well. 

July 2021 update: The scripts were re-written in python, generally following the same logic and creating the same outcome with a few minor tweaks (such as with file naming standards).

# Requirements

Install the following packages through the commandline:

- `pip install pandas`
- `pip install sodapy`

# Usage

1. Upload the annual budget to `data/approved_budget/` and/or `data/proposed_budget/`.
    - IMPORTANT: Include a .csv copy of each spreadsheet (the script does not take .xlsx, only .csv)

1. Optional: this step is only needed if you are going to be pushing data back to the Socrata LA City Open Data Portal. If not, then skip to the next step.
    - Enter your username, password, and [app token](https://support.socrata.com/hc/en-us/articles/210138558-Generating-an-App-Token) in `credentials.lahub_user`, `credentials.lahub_pass`, `credentials.lahub_auth` respectively.
    - Open the desired script in your text editor of choice. Search for the comment "uncomment if you are going to log in / push to the data portal" and uncomment those lines.

1. There are a few minimal changes to make to customize the script to the current year's budget, including:
    - update the filepaths to `data/approved_budget/...` etc.
    - make sure the relevant budget spreadsheets follow the same column titles/orders as in the previous year; if they are not, then adjust the script to match the new columns.

1. `cd` into `scripts/python-scripts` and run the relevant scripts.
    
    Example usages
   - `python3 expenses.py`
   - `python3 revenue.py`
   - `python3 open_budget_other.py`
   - `python3 department_and_program_descriptions.py`

1. Any output files will be saved to the same filepath as the current budget