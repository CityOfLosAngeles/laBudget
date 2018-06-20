# parse_revenues.py

# import libraries

# for changing working directory
import os
# for reading PDF text
import PyPDF2
# for regular expression matching
import re

# set directory
os.chdir('/Users/adamscherling/github/laBudget/proposed_budget/data/FY18-19')

# pull text from pdf file
pdfFileObject = open('05-Exhibit B 19P.pdf', 'rb')
pdfReader = PyPDF2.PdfFileReader(pdfFileObject)

# combine text from all pages into a single string
count = pdfReader.numPages
pdfText = ''
for i in range(count):
    page = pdfReader.getPage(i)
    pdfText = pdfText + page.extractText()

# pick out the text for General Receipts and Special Receipts
start = pdfText.find("General Receipts:")
end = pdfText.find("Available Balances:")
pdfText = pdfText[start:end]
print(start, end)

# remove gratuitous newline characters, commas, $, %
pdfText = pdfText.replace('\n', '')
pdfText = pdfText.replace(',', '')
pdfText = pdfText.replace('$', '')
pdfText = pdfText.replace('%', '')

end = pdfText.find("Total General Receipts")
GF_text = pdfText[:end]


start = pdfText.find("Special Receipts:")
end = pdfText.find("Total Special Receipts...")
SF_text = pdfText[start:end]

# remove the dots
# https://stackoverflow.com/questions/14488557/remove-consecutive-dotsperiods-from-a-string
consecutivedots = re.compile(r'\.{3,}')
GF_text = consecutivedots.sub(',', GF_text)
SF_text = consecutivedots.sub(',', SF_text)

# convert space between numbers to commas
spaceBetweenNumbers = re.compile(r'(?:\d)(\ {3,})(?:\d)')
GF_text = spaceBetweenNumbers.sub(',', GF_text)
