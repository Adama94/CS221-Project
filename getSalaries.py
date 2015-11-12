import csv,collections

with open('2015W9.txt') as inputfile:
	results = list(csv.reader(inputfile))
salaries = {}
for i in range(1,len(results)):
	line = results[i]
	if line[4] == 'Def':
		continue
	firstName = line[4]
	lastName = line[3]
	salary = line[10]
	salaries['%s %s' %(firstName,lastName)] = salary
print salaries['Andrew Luck']
