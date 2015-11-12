import nflgame, csv
import numpy as np

# General code for representing a weighted CSP (Constraint Satisfaction Problem).
# All variables are being referenced by their index instead of their original
# names.
class CSP:
    def __init__(self):
        # Total number of variables in the CSP.
        self.numVars = 0

        # The list of variable names in the same order as they are added. A
        # variable name can be any hashable objects, for example: int, str,
        # or any tuple with hashtable objects.
        self.variables = []

        # Each key K in this dictionary is a variable name.
        # values[K] is the list of domain values that variable K can take on.
        self.values = {}

        # Each entry is a unary factor table for the corresponding variable.
        # The factor table corresponds to the weight distribution of a variable
        # for all added unary factor functions. If there's no unary function for 
        # a variable K, there will be no entry for K in unaryFactors.
        # E.g. if B \in ['a', 'b'] is a variable, and we added two
        # unary factor functions f1, f2 for B,
        # then unaryFactors[B]['a'] == f1('a') * f2('a')
        self.unaryFactors = {}

        # Each entry is a dictionary keyed by the name of the other variable
        # involved. The value is a binary factor table, where each table
        # stores the factor value for all possible combinations of
        # the domains of the two variables for all added binary factor
        # functions. The table is represented as a dictionary of dictionary.
        #
        # As an example, if we only have two variables
        # A \in ['b', 'c'],  B \in ['a', 'b']
        # and we've added two binary functions f1(A,B) and f2(A,B) to the CSP,
        # then binaryFactors[A][B]['b']['a'] == f1('b','a') * f2('b','a').
        # binaryFactors[A][A] should return a key error since a variable
        # shouldn't have a binary factor table with itself.

        self.binaryFactors = {}

    def add_variable(self, var, domain):
        """
        Add a new variable to the CSP.
        """
        if var in self.variables:
            raise Exception("Variable name already exists: %s" % str(var))

        self.numVars += 1
        self.variables.append(var)
        self.values[var] = domain
        self.unaryFactors[var] = None
        self.binaryFactors[var] = dict()


    def get_neighbor_vars(self, var):
        """
        Returns a list of variables which are neighbors of |var|.
        """
        return self.binaryFactors[var].keys()

    def add_unary_factor(self, var, factorFunc):
        """
        Add a unary factor function for a variable. Its factor
        value across the domain will be *merged* with any previously added
        unary factor functions through elementwise multiplication.

        How to get unary factor value given a variable |var| and
        value |val|?
        => csp.unaryFactors[var][val]
        """
        factor = {val:float(factorFunc(val)) for val in self.values[var]}
        if self.unaryFactors[var] is not None:
            assert len(self.unaryFactors[var]) == len(factor)
            self.unaryFactors[var] = {val:self.unaryFactors[var][val] * \
                factor[val] for val in factor}
        else:
            self.unaryFactors[var] = factor

    def add_binary_factor(self, var1, var2, factor_func):
        """
        Takes two variable names and a binary factor function
        |factorFunc|, add to binaryFactors. If the two variables already
        had binaryFactors added earlier, they will be *merged* through element
        wise multiplication.

        How to get binary factor value given a variable |var1| with value |val1| 
        and variable |var2| with value |val2|?
        => csp.binaryFactors[var1][var2][val1][val2]
        """
        # never shall a binary factor be added over a single variable
        try:
            assert var1 != var2
        except:
            print '!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!'
            print '!! Tip:                                                                       !!'
            print '!! You are adding a binary factor over a same variable...                  !!'
            print '!! Please check your code and avoid doing this.                               !!'
            print '!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!'
            raise

        self.update_binary_factor_table(var1, var2,
            {val1: {val2: float(factor_func(val1, val2)) \
                for val2 in self.values[var2]} for val1 in self.values[var1]})
        self.update_binary_factor_table(var2, var1, \
            {val2: {val1: float(factor_func(val1, val2)) \
                for val1 in self.values[var1]} for val2 in self.values[var2]})

    def update_binary_factor_table(self, var1, var2, table):
        """
        Private method you can skip for 0c, might be useful for 1c though.
        Update the binary factor table for binaryFactors[var1][var2].
        If it exists, element-wise multiplications will be performed to merge
        them together.
        """
        if var2 not in self.binaryFactors[var1]:
            self.binaryFactors[var1][var2] = table
        else:
            currentTable = self.binaryFactors[var1][var2]
            for i in table:
                for j in table[i]:
                    assert i in currentTable and j in currentTable[i]
                    currentTable[i][j] *= table[i][j]

# A backtracking algorithm that solves weighted CSP.
# Usage:
#   search = BacktrackingSearch()
#   search.solve(csp)
class BacktrackingSearch():

    def reset_results(self):
        """
        This function resets the statistics of the different aspects of the
        CSP solver. We will be using the values here for grading, so please
        do not make any modification to these variables.
        """
        # Keep track of the best assignment and weight found.
        self.optimalAssignment = {}
        self.optimalWeight = 0

        # Keep track of the number of optimal assignments and assignments. These
        # two values should be identical when the CSP is unweighted or only has binary
        # weights.
        self.numOptimalAssignments = 0
        self.numAssignments = 0

        # Keep track of the number of times backtrack() gets called.
        self.numOperations = 0

        # Keep track of the number of operations to get to the very first successful
        # assignment (doesn't have to be optimal).
        self.firstAssignmentNumOperations = 0

        # List of all solutions found.
        self.allAssignments = []

    def print_stats(self):
        """
        Prints a message summarizing the outcome of the solver.
        """
        if self.optimalAssignment:
            print "Found %d optimal assignments with weight %f in %d operations" % \
                (self.numOptimalAssignments, self.optimalWeight, self.numOperations)
            print "First assignment took %d operations" % self.firstAssignmentNumOperations
        else:
            print "No solution was found."

    def get_delta_weight(self, assignment, var, val):
        """
        Given a CSP, a partial assignment, and a proposed new value for a variable,
        return the change of weights after assigning the variable with the proposed
        value.

        @param assignment: A dictionary of current assignment. Unassigned variables
            do not have entries, while an assigned variable has the assigned value
            as value in dictionary. e.g. if the domain of the variable A is [5,6],
            and 6 was assigned to it, then assignment[A] == 6.
        @param var: name of an unassigned variable.
        @param val: the proposed value.

        @return w: Change in weights as a result of the proposed assignment. This
            will be used as a multiplier on the current weight.
        """
        assert var not in assignment
        w = 1.0
        if self.csp.unaryFactors[var]:
            w *= self.csp.unaryFactors[var][val]
            if w == 0: return w
        for var2, factor in self.csp.binaryFactors[var].iteritems():
            if var2 not in assignment: continue  # Not assigned yet
            w *= factor[val][assignment[var2]]
            if w == 0: return w
        return w

    def solve(self, csp, mcv = False, ac3 = False):
        """
        Solves the given weighted CSP using heuristics as specified in the
        parameter. Note that unlike a typical unweighted CSP where the search
        terminates when one solution is found, we want this function to find
        all possible assignments. The results are stored in the variables
        described in reset_result().

        @param csp: A weighted CSP.
        @param mcv: When enabled, Most Constrained Variable heuristics is used.
        @param ac3: When enabled, AC-3 will be used after each assignment of an
            variable is made.
        """
        # CSP to be solved.
        self.csp = csp

        # Set the search heuristics requested asked.
        self.mcv = mcv
        self.ac3 = ac3

        # Reset solutions from previous search.
        self.reset_results()

        # The dictionary of domains of every variable in the CSP.
        self.domains = {var: list(self.csp.values[var]) for var in self.csp.variables}

        # Perform backtracking search.
        self.backtrack({}, 0, 1)
        # Print summary of solutions.
        self.print_stats()

    def calculateScore(self, assignment):
        score = 0
        for position in assignment:
            score += assignment[position][1]
        return score

    def backtrack(self, assignment, numAssigned, weight):
        """
        Perform the back-tracking algorithms to find all possible solutions to
        the CSP.

        @param assignment: A dictionary of current assignment. Unassigned variables
            do not have entries, while an assigned variable has the assigned value
            as value in dictionary. e.g. if the domain of the variable A is [5,6],
            and 6 was assigned to it, then assignment[A] == 6.
        @param numAssigned: Number of currently assigned variables
        @param weight: The weight of the current partial assignment.
        """ 
        if len(self.allAssignments) >= 1000:
            return

        score = self.calculateScore(assignment)
        if score > 60000:
            return

        maxSalary = 10000
        if score + (9 - numAssigned) * maxSalary < 60000:
            return 

        minSalary = 4000
        if score + (9 - numAssigned) * minSalary > 60000:
            return 

        self.numOperations += 1
        assert weight > 0
        if numAssigned == self.csp.numVars:
            # A satisfiable solution have been found. Update the statistics.            
            self.numAssignments += 1
            newAssignment = {}
            for var in self.csp.variables:
                newAssignment[var] = assignment[var]
            self.allAssignments.append(newAssignment)

            if len(self.optimalAssignment) == 0 or weight >= self.optimalWeight:
                if weight == self.optimalWeight:
                    self.numOptimalAssignments += 1
                else:
                    self.numOptimalAssignments = 1
                self.optimalWeight = weight

                self.optimalAssignment = newAssignment
                if self.firstAssignmentNumOperations == 0:
                    self.firstAssignmentNumOperations = self.numOperations
            return

        # Select the next variable to be assigned.
        var = self.get_unassigned_variable(assignment)
        # Get an ordering of the values.
        ordered_values = self.domains[var]

        # Continue the backtracking recursion using |var| and |ordered_values|.
        if not self.ac3:
            # When arc consistency check is not enabled.
            for val in ordered_values:
                deltaWeight = self.get_delta_weight(assignment, var, val)
                if deltaWeight > 0:
                    assignment[var] = val
                    self.backtrack(assignment, numAssigned + 1, weight * deltaWeight)
                    del assignment[var]
        else:
            # Arc consistency check is enabled.
            # Problem 1c: skeleton code for AC-3
            # You need to implement arc_consistency_check().
            for val in ordered_values:
                deltaWeight = self.get_delta_weight(assignment, var, val)
                if deltaWeight > 0:
                    assignment[var] = val
                    # create a deep copy of domains as we are going to look
                    # ahead and change domain values
                    localCopy = copy.deepcopy(self.domains)
                    # fix value for the selected variable so that hopefully we
                    # can eliminate values for other variables
                    self.domains[var] = [val]

                    # enforce arc consistency
                    self.arc_consistency_check(var)

                    self.backtrack(assignment, numAssigned + 1, weight * deltaWeight)
                    # restore the previous domains
                    self.domains = localCopy
                    del assignment[var]

    def get_unassigned_variable(self, assignment):
        """
        Given a partial assignment, return a currently unassigned variable.

        @param assignment: A dictionary of current assignment. This is the same as
            what you've seen so far.

        @return var: a currently unassigned variable.
        """

        if not self.mcv:
            # Select a variable without any heuristics.
            for var in self.csp.variables:
                if var not in assignment: return var
        else:
            # Problem 1b
            # Heuristic: most constrained variable (MCV)
            # Select a variable with the least number of remaining domain values.
            # Hint: given var, self.domains[var] gives you all the possible values
            # Hint: get_delta_weight gives the change in weights given a partial
            #       assignment, a variable, and a proposed value to this variable
            
            # BEGIN_YOUR_CODE (around 10 lines of code expected)
            mcv = None
            minConsistentAssignments = None
            for var in self.csp.variables:
                if var not in assignment:
                    numConsistentAssignments = 0
                    for a in self.domains[var]:
                        if not self.get_delta_weight(assignment, var, a) == 0:
                            numConsistentAssignments += 1

                    if mcv == None or numConsistentAssignments < minConsistentAssignments:
                        mcv = var
                        minConsistentAssignments = numConsistentAssignments
            return mcv
            # END_YOUR_CODE

    def arc_consistency_check(self, var):
        """
        Perform the AC-3 algorithm. The goal is to reduce the size of the
        domain values for the unassigned variables based on arc consistency.

        @param var: The variable whose value has just been set.
        """
        # Problem 1c
        # Hint: How to get variables neighboring variable |var|?
        # => for var2 in self.csp.get_neighbor_vars(var):
        #       # use var2
        #
        # Hint: How to check if two values are inconsistent?
        # For unary factors
        #   => self.csp.unaryFactors[var1][val1] == 0
        #
        # For binary factors
        #   => self.csp.binaryFactors[var1][var2][val1][val2] == 0
        #   (self.csp.binaryFactors[var1][var2] returns a nested dict of all assignments)

        # BEGIN_YOUR_CODE (around 20 lines of code expected)
        def enforceArcConsistency(X_i, X_j):           
            valuesToRemove = []
            for value_i in self.domains[X_i]:
                shouldAdd = True
                for value_j in self.domains[X_j]:
                    if not self.csp.binaryFactors[X_i][X_j][value_i][value_j] == 0:
                        shouldAdd = False
                if shouldAdd:
                    valuesToRemove.append(value_i)
            for val in valuesToRemove:
                self.domains[X_i].remove(val)

        queue = [var]
        while queue:
            var1 = queue.pop(0)
            for var2 in self.csp.get_neighbor_vars(var1):
                domain_var2 = set(self.domains[var2])
                enforceArcConsistency(var2, var1)
                if set(self.domains[var2]) != domain_var2:
                    queue.append(var2)
        # END_YOUR_CODE

# Returns sum variable on the variables 
def get_sum_variable(csp, name, variables, maxSum):
    """
    Given a list of |variables| each with non-negative integer domains,
    returns the name of a new variable with domain range(0, maxSum+1), such that
    it's consistent with the value |n| iff the assignments for |variables|
    sums to |n|.

    @param name: Prefix of all the variables that are going to be added.
        Can be any hashable objects. For every variable |var| added in this
        function, it's recommended to use a naming strategy such as
        ('sum', |name|, |var|) to avoid conflicts with other variable names.
    @param variables: A list of variables that are already in the CSP that
        have non-negative integer values as its domain.
    @param maxSum: An integer indicating the maximum sum value allowed. You
        can use it to get the auxiliary variables' domain

    @return result: The name of a newly created variable with domain range
        [0, maxSum] such that it's consistent with an assignment of |n|
        iff the assignment of |variables| sums to |n|.
    """
    # BEGIN_YOUR_CODE (around 20 lines of code expected)
    domain = []
    for i in np.arange(0, maxSum + 1, 100):
        for j in np.arange(i, maxSum + 1, 100):
            domain.append((i, j))

    for var in variables:
        csp.add_variable(('sum', name, var), domain)

    for i in range(len(variables)):                    
        if i == 0:
            csp.add_unary_factor(('sum', name, variables[i]), lambda x: x[0] == 0)
        else:
            csp.add_binary_factor(('sum', name, variables[i - 1]), ('sum', name, variables[i]), lambda x,y : x[1] == y[0])         

        csp.add_binary_factor(('sum', name, variables[i]), variables[i], lambda x,y : x[1] == x[0] + y[1])

    domain = np.arange(0, maxSum + 1, 100)
    newVarName = ('sum', name, 'newVarName')    
    csp.add_variable(newVarName, domain)
    
    csp.add_binary_factor(('sum', name, variables[len(variables) - 1]), newVarName, lambda x,y : x[1] == y)
    return newVarName
    # END_YOUR_CODE

def getSalariesAndPositions(filename):
    with open(filename) as inputfile:
        results = list(csv.reader(inputfile))
    salaries = {}
    positions = {}
    scores = {}
    for i in range(1,len(results) - 1):
        line = results[i]
        if line[4] == 'Def':
            name = line[3]
            salary = line[9]
            position = line[4]
            score = line[8]
        else:
            firstName = line[4]
            lastName = line[3]
            name = '%s %s' %(firstName,lastName)
            salary = line[10]
            position = line[5]
            score = line[9]

        if not salary == '' and not position == '':
            salaries[name] = int(salary)
            positions[name] = position
            scores[name] = float(score)

    return salaries, positions, scores

def createCSPWithVariables(week, year):
    csp = CSP()
    filename = str(year) + "W" + str(week) + ".txt"
    salaries, positions, scores = getSalariesAndPositions(filename)

    TE_domain = []
    RB_domain = []
    WR_domain = []
    K_domain = []
    QB_domain = []
    Defense_domain = []

    for player in salaries: 
        position = positions[player]
        salary = salaries[player]

        if position == "QB":
            QB_domain.append((player, salary))
        if position == "RB":
            RB_domain.append((player, salary))
        if position == "WR":
            WR_domain.append((player, salary))
        if position == "TE":
            TE_domain.append((player, salary))
        if position == "PK":
            K_domain.append((player, salary))
        if position == "Def":
            Defense_domain.append((player, salary))
    
    csp.add_variable("QB", QB_domain)
    csp.add_variable("RB1", RB_domain)
    csp.add_variable("RB2", RB_domain)
    csp.add_variable("WR1", WR_domain)
    csp.add_variable("WR2", WR_domain)
    csp.add_variable("WR3", WR_domain)
    csp.add_variable("TE", TE_domain)
    csp.add_variable("K", K_domain)
    csp.add_variable("D", Defense_domain)

    return csp, scores

def addConstraints(csp, salaryCap):
    csp.add_binary_factor("RB1", "RB2", lambda x,y: x != y)
    csp.add_binary_factor("WR1", "WR2", lambda x,y: x != y)
    csp.add_binary_factor("WR2", "WR3", lambda x,y: x != y)
    csp.add_binary_factor("WR1", "WR3", lambda x,y: x != y)
    variables = ["QB", "RB1", "RB2", "WR1", "WR2", "WR3", "K", "D", "TE"]

csp, scores = createCSPWithVariables(9, 2015)
salaryCap = 60000
addConstraints(csp, salaryCap)
search = BacktrackingSearch()
search.solve(csp)

def computeScore(scores, assignment):
    score = 0
    for position in assignment:        
        player = assignment[position][0]        
        score += scores[player]
    return score

computedScores = []
for assignment in search.allAssignments:
    score = computeScore(scores, assignment)
    computedScores.append(score)
print max(computedScores)
print min(computedScores)
print np.average(computedScores)

numWinners = 0
for i in range(len(computedScores)): 
    if computedScores[i] >= 111.21:
        numWinners += 1
print numWinners

print search.allAssignments[1], computeScore(scores, search.allAssignments[1]) 
print search.allAssignments[500], computeScore(scores, search.allAssignments[500])

