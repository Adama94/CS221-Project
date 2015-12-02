import csv

def getProjections(filename):
    with open(filename) as inputfile:
        results = list(csv.reader(inputfile))
    projections = {}
    risks = {}
    for i in range(1,len(results) - 1):
        line = results[i]
        name = ''
        projection = ''
        if line[3] == 'DST':
            name = line[2] + 'Defense'
        else:
            name = line[2]
        projection = line[8]
        projections[name] = float(projection)
        risk = line[21]
        if risk != 'null':
            risks[name] = float(risk)
    return projections

for week in range(1,10):
    filename = 'FFA-CustomRankings2015W%s.csv' %(week)
    projections = getProjections(filename)
    if 'Aaron Rodgers' in projections:
        print projections['Aaron Rodgers']
    else:
        print 'bye/injured'