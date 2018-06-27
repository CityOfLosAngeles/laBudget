# parse_revenues.py

# import libraries

# for changing working directory
import os
# for reading PDF text
import PyPDF2
# for regular expression matching
import re

# set directory
os.chdir('/Users/adamscherling/github/laBudget/data/proposed_budget/FY18-19')

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
# end = pdfText.find("Available Balances:")
pdfText = pdfText[start:]

# remove gratuitous newline characters, commas, $, %
pdfText = pdfText.replace('\n', '')
pdfText = pdfText.replace(',', '')
pdfText = pdfText.replace('$', '')
pdfText = pdfText.replace('%', '')

end = pdfText.find("Total General Receipts")
GF_receipts = pdfText[17:end]

start = pdfText.find("Special Receipts:")
end = pdfText.find("Total Special Receipts...")
SF_receipts = pdfText[(start+17):end]

start = pdfText.find("Available Balances:")
end = pdfText.find("Total Available Balances...")
SF_balances = pdfText[(start+19):end]

print(GF_receipts)
print('***')
print(SF_receipts)
print('***')
print(SF_balances)


# remove column titles
colTitles = re.compile(r'EXHIBIT B|BUDGET SUMMARY|RECEIPTS| of Total| ofTotal|Total')
GF_receipts = colTitles.sub('', GF_receipts)
SF_receipts = colTitles.sub('', SF_receipts)
SF_balances = colTitles.sub('', SF_balances)

# convert double hyphens after a period to a zero
doubleHyphen = re.compile(r'\.--')
GF_receipts = doubleHyphen.sub('0', GF_receipts)
SF_receipts = doubleHyphen.sub('0', SF_receipts)
SF_balances = doubleHyphen.sub('0', SF_balances)

# remove the dots
# https://stackoverflow.com/questions/14488557/remove-consecutive-dotsperiods-from-a-string
consecutivedots = re.compile(r'\.{3,}')
GF_receipts = consecutivedots.sub(',', GF_receipts)
SF_receipts = consecutivedots.sub(',', SF_receipts)
SF_balances = consecutivedots.sub(',', SF_balances)

# convert space between numbers to commas
spaceBetweenNumbers = re.compile(r'(\d)(\ {1,})(\d)')
GF_receipts = spaceBetweenNumbers.sub(r'\1,\3', GF_receipts)
SF_receipts = spaceBetweenNumbers.sub(r'\1,\3', SF_receipts)
SF_balances = spaceBetweenNumbers.sub(r'\1,\3', SF_balances)

# insert newlines wherever a digit meets a letter
digitMeetsLetter = re.compile(r'(\d)([A-Z])')
GF_receipts = digitMeetsLetter.sub(r'\1\n\2', GF_receipts)
SF_receipts = digitMeetsLetter.sub(r'\1\n\2', SF_receipts)
SF_balances = digitMeetsLetter.sub(r'\1\n\2', SF_balances)

# remove spaces before commas
spaceBeforeComma = re.compile(r'\ ,')
GF_receipts = spaceBeforeComma.sub(',', GF_receipts)
SF_receipts = spaceBeforeComma.sub(',', SF_receipts)
SF_balances = spaceBeforeComma.sub(',', SF_balances)


print(GF_receipts)
print('***')
print(SF_receipts)
print('***')
print(SF_balances)

pdfFileObject.close()

# write the files to CSV
gf = open('gf_receipts.csv', 'w')
gf.write(GF_receipts)
gf.close()

sf1 = open('sf_receipts.csv', 'w')
sf1.write(SF_receipts)
sf1.close()

sf2 = open('sf_balances.csv', 'w')
sf2.write(SF_balances)
sf2.close()



