import csv
import sys
import os
# sys.path.insert(1, os.path.realpath(os.path.pardir))
import lwb
import config


with open('data/deltmp.csv', 'r', encoding="utf-8") as csvfile:
	dellist = csv.DictReader(csvfile)

	count = 0
	for row in dellist:
		count +=1
		print('\n['+str(count)+']: ')
		lwb.removeclaim(row['del'])
