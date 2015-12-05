import csv

def getSalariesAndPositions(filename):
    with open(filename) as inputfile:
        results = list(csv.reader(inputfile))
    salaries = {}
    positions = {}
    scores = {}
    for i in range(1,len(results) - 1):
        line = results[i]
        if line[4] == 'Def':
            if line[5] == 'nwe':
                line[5] = 'ne'
            if line[5] == 'kan':
                line[5] = 'kc'
            if line[5] == 'nor':
                line[5] = 'no'
            if line[5] == 'gnb':
                line[5] = 'gb'
            if line[5] == 'tam':
                line[5] = 'tb'
            if line[5] == 'sfo':
                line[5] = 'sf'
            if line[5] == 'sdg':
                line[5] = 'sd'
            name = line[5]+'Defense'
            salary = line[9]
            position = line[4]
            score = line[8]
        else:
            firstName = line[4]
            lastName = line[3]
            name = '%s %s' %(firstName,lastName)
            if name == 'Odell BeckhamJr.':
                name = 'Odell Beckham'
            salary = line[10]
            position = line[5]
            score = line[9]

        if not salary == '' and not position == '':
            salaries[name] = int(salary)
            positions[name] = position
            scores[name] = float(score)

    return salaries, positions, scores

def getFutureSalariesAndPositions(filename):
    with open(filename) as inputfile:
        results = list(csv.reader(inputfile))
    salaries = {}
    positions = {}
    for i in range(1,len(results) - 1):
        line = results[i]
        if line[1] == 'D':
            name = line[8].lower()+'Defense'
            salary = line[6]
            position = "Def"
        elif line[1] == 'K':
            firstName = line[2]
            lastName = line[3]
            name = '%s %s' %(firstName,lastName)
            salary = line[6]
            position = 'PK'
        else:
            firstName = line[2]
            lastName = line[3]
            name = '%s %s' %(firstName,lastName)
            if name == 'Odell Beckham Jr.':
                name = 'Odell Beckham'
            salary = line[6]
            position = line[1]

        if not salary == '' and not position == '':
            salaries[name] = int(salary)
            positions[name] = position

    scores = {}
    return salaries, positions, scores