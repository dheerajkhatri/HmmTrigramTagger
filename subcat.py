import re
import sys

def subcategorize(word):
	if not re.search(r'\w',word):
		return '<PUNCS>'
	elif re.search(r'[A-Z]',word):
		return '<CAPITAL>'
	elif re.search(r'\d',word):
		return '<NUM>'
	elif re.search(r'(ion\b|ty\b|ics\b|ment\b|ence\b|ance\b|ness\b|ist\b|ism\b)',word):
		return '<NOUNLIKE>'
	elif re.search(r'(ate\b|fy\b|ize\b|\ben|\bem)',word):
		return '<VERBLIKE>'
	elif re.search(r'(\bun|\bin|ble\b|ry\b|ish\b|ious\b|ical\b|\bnon)',word):
		return '<JJLIKE>'
	else:
		return '<OTHER>'

print subcategorize(sys.argv[1])		