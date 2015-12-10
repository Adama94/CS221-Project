# A backtracking algorithm that solves weighted CSP.
# Usage:
#   search = BacktrackingSearch()
#   search.solve(csp)

import numpy as np
import random

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
        # if self.optimalAssignment:
        #     print "Found %d optimal assignments with weight %f in %d operations" % \
        #         (self.numOptimalAssignments, self.optimalWeight, self.numOperations)
        #     print "First assignment took %d operations" % self.firstAssignmentNumOperations
        # else:
        #     print "No solution was found."

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

    def solve(self, csp, numLineups, ep_greedy, comparisonIndex, mcv = False, ac3 = False):
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

        # Set the total number of lineups to generate
        self.numLineups = numLineups

        # Set the epsilon-greedy probability
        self.ep_greedy = ep_greedy

        # Comparison index
        self.comparisonIndex = comparisonIndex

        # Perform backtracking search.
        if ep_greedy < 0.0:
            while len(self.allAssignments) < self.numLineups:
                self.backtrack({}, 0, 1, numLineups)
        else:
            self.backtrack({}, 0, 1, numLineups)
        # Print summary of solutions.
        self.print_stats()

    def calculateScore(self, assignment):
        score = 0
        for position in assignment:
            score += assignment[position][1]
        return score

    def backtrack(self, assignment, numAssigned, weight, numLineupsPerPlayer):
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
        if len(self.allAssignments) >= self.numLineups:
            return

        score = self.calculateScore(assignment)

        if score > 60000:
            return

        maxSalary = 9400
        if score + (9 - numAssigned) * maxSalary < 58000:
            return 

        minSalary = 4000
        if score + (9 - numAssigned) * minSalary > 60000:
            return 

        self.numOperations += 1
        assert weight > 0
        if numAssigned == self.csp.numVars:
            # A satisfiable solution have been found. Update the statistics.            
            # if len(self.allAssignments) % 1000 == 0:
            #     print len(self.allAssignments)
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
        ordered_values = []
        p = None

        # Efficiency-based algorithm - not based on epsilon-greedy at all
        if self.ep_greedy < 0.0:
            efficiency_list = [player[3] for player in self.domains[var]]
            efficiency_sum = sum(efficiency_list)
            efficiency_list = map(lambda x: x / efficiency_sum, efficiency_list)
            pick = list(np.random.multinomial(1, efficiency_list))
            ordered_values.append(self.domains[var][pick.index(1)])

        # Epsilon-Greedy Algorithm - deterministic will sort by efficiency, random will choose
        # from a multinomial distribution based on the salaries of each player
        else:
            p = np.random.random_sample()
            if p <= self.ep_greedy:
                ordered_values = sorted(self.domains[var], key=lambda tup: tup[self.comparisonIndex],reverse=True)
            else:
                salary_array = []
                curr_players = assignment.values()
                players = []
                for player in self.domains[var]:
                    if player not in curr_players:
                        players.append(player)
                        salary_array.append(float(player[self.comparisonIndex]))

                salary_sum = sum(salary_array)
                prob_array = map(lambda x: x / salary_sum, salary_array)
                stones = np.random.multinomial(numLineupsPerPlayer, prob_array)
                ordered_values = {players[i]:stones[i] for i in range(0, len(stones)) if stones[i] > 0}

        # Continue the backtracking recursion using |var| and |ordered_values|.
        if not self.ac3:
            # When arc consistency check is not enabled.
            for val in ordered_values:
                deltaWeight = self.get_delta_weight(assignment, var, val)
                if deltaWeight > 0:
                    assignment[var] = val
                    self.backtrack(assignment, numAssigned + 1, weight * deltaWeight, \
                        ordered_values[val] if (self.ep_greedy is not -1 and p > self.ep_greedy) else numLineupsPerPlayer)
                    del assignment[var]
        # else:
        #     # Arc consistency check is enabled.
        #     # Problem 1c: skeleton code for AC-3
        #     # You need to implement arc_consistency_check().
        #     for val in ordered_values:
        #         deltaWeight = self.get_delta_weight(assignment, var, val)
        #         if deltaWeight > 0:
        #             assignment[var] = val
        #             # create a deep copy of domains as we are going to look
        #             # ahead and change domain values
        #             localCopy = copy.deepcopy(self.domains)
        #             # fix value for the selected variable so that hopefully we
        #             # can eliminate values for other variables
        #             self.domains[var] = [val]

        #             # enforce arc consistency
        #             self.arc_consistency_check(var)

        #             self.backtrack(assignment, numAssigned + 1, weight * deltaWeight, \
        #                 ordered_values[val] if (self.ep_greedy is not -1 and p > self.ep_greedy) else numLineupsPerPlayer)
        #             # restore the previous domains
        #             self.domains = localCopy
        #             del assignment[var]

    def get_unassigned_variable(self, assignment):
        """
        Given a partial assignment, return a currently unassigned variable.

        @param assignment: A dictionary of current assignment. This is the same as
            what you've seen so far.

        @return var: a currently unassigned variable.
        """

        # for var in self.csp.variables:
        #     if var not in assignment: return var
        choices = []
        for var in self.csp.variables:
            if var not in assignment:
                choices.append(var)
        var = random.choice(choices)
        return var

    # def arc_consistency_check(self, var):
    #     """
    #     Perform the AC-3 algorithm. The goal is to reduce the size of the
    #     domain values for the unassigned variables based on arc consistency.

    #     @param var: The variable whose value has just been set.
    #     """
    #     # Problem 1c
    #     # Hint: How to get variables neighboring variable |var|?
    #     # => for var2 in self.csp.get_neighbor_vars(var):
    #     #       # use var2
    #     #
    #     # Hint: How to check if two values are inconsistent?
    #     # For unary factors
    #     #   => self.csp.unaryFactors[var1][val1] == 0
    #     #
    #     # For binary factors
    #     #   => self.csp.binaryFactors[var1][var2][val1][val2] == 0
    #     #   (self.csp.binaryFactors[var1][var2] returns a nested dict of all assignments)

    #     # BEGIN_YOUR_CODE (around 20 lines of code expected)
    #     def enforceArcConsistency(X_i, X_j):           
    #         valuesToRemove = []
    #         for value_i in self.domains[X_i]:
    #             shouldAdd = True
    #             for value_j in self.domains[X_j]:
    #                 if not self.csp.binaryFactors[X_i][X_j][value_i][value_j] == 0:
    #                     shouldAdd = False
    #             if shouldAdd:
    #                 valuesToRemove.append(value_i)
    #         for val in valuesToRemove:
    #             self.domains[X_i].remove(val)

    #     queue = [var]
    #     while queue:
    #         var1 = queue.pop(0)
    #         for var2 in self.csp.get_neighbor_vars(var1):
    #             domain_var2 = set(self.domains[var2])
    #             enforceArcConsistency(var2, var1)
    #             if set(self.domains[var2]) != domain_var2:
    #                 queue.append(var2)
    #     # END_YOUR_CODE