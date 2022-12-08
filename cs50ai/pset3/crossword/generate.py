import sys
import copy

from crossword import *
from helpers import *


class CrosswordCreator():

    def __init__(self, crossword):
        """
        Create new CSP crossword generate.
        """
        self.crossword = crossword
        self.domains = {
            var: self.crossword.words.copy()
            for var in self.crossword.variables
        }

    def letter_grid(self, assignment):
        """
        Return 2D array representing a given assignment.
        """
        letters = [
            [None for _ in range(self.crossword.width)]
            for _ in range(self.crossword.height)
        ]
        for variable, word in assignment.items():
            direction = variable.direction
            for k in range(len(word)):
                i = variable.i + (k if direction == Variable.DOWN else 0)
                j = variable.j + (k if direction == Variable.ACROSS else 0)
                letters[i][j] = word[k]
        return letters

    def print(self, assignment):
        """
        Print crossword assignment to the terminal.
        """
        letters = self.letter_grid(assignment)
        for i in range(self.crossword.height):
            for j in range(self.crossword.width):
                if self.crossword.structure[i][j]:
                    print(letters[i][j] or " ", end="")
                else:
                    print("█", end="")
            print()

    def save(self, assignment, filename):
        """
        Save crossword assignment to an image file.
        """
        from PIL import Image, ImageDraw, ImageFont
        cell_size = 100
        cell_border = 2
        interior_size = cell_size - 2 * cell_border
        letters = self.letter_grid(assignment)

        # Create a blank canvas
        img = Image.new(
            "RGBA",
            (self.crossword.width * cell_size,
             self.crossword.height * cell_size),
            "black"
        )
        font = ImageFont.truetype("assets/fonts/OpenSans-Regular.ttf", 80)
        draw = ImageDraw.Draw(img)

        for i in range(self.crossword.height):
            for j in range(self.crossword.width):

                rect = [
                    (j * cell_size + cell_border,
                     i * cell_size + cell_border),
                    ((j + 1) * cell_size - cell_border,
                     (i + 1) * cell_size - cell_border)
                ]
                if self.crossword.structure[i][j]:
                    draw.rectangle(rect, fill="white")
                    if letters[i][j]:
                        w, h = draw.textsize(letters[i][j], font=font)
                        draw.text(
                            (rect[0][0] + ((interior_size - w) / 2),
                             rect[0][1] + ((interior_size - h) / 2) - 10),
                            letters[i][j], fill="black", font=font
                        )

        img.save(filename)

    def solve(self):
        """
        Enforce node and arc consistency, and then solve the CSP.
        """
        self.enforce_node_consistency()
        self.ac3()
        return self.backtrack(dict())

    def enforce_node_consistency(self):
        """
        Update `self.domains` such that each variable is node-consistent.
        (Remove any values that are inconsistent with a variable's unary
         constraints; in this case, the length of the word.)
        """
        for key in self.domains:
            for domain in copy.deepcopy(self.domains[key]):
                if key.length != len(domain):
                    self.domains[key].remove(domain)

    def revise(self, x, y):
        """
        Make variable `x` arc consistent with variable `y`.
        To do so, remove values from `self.domains[x]` for which there is no
        possible corresponding value for `y` in `self.domains[y]`.

        Return True if a revision was made to the domain of `x`; return
        False if no revision was made.
        """
        revised = False
        # If arc is none, there is no arc
        if self.crossword.overlaps[(x, y)] == None:
            return revised

        # Find overlap character of each domain
        overlap = self.crossword.overlaps[(x, y)]
        charX = overlap[0]
        charY = overlap[1]

        # Check if each of the domains in x matches with a domain in y
        for domainX in copy.deepcopy(self.domains[x]):
            found = False
            for domainY in self.domains[y]:
                if len(domainY) > charY and len(domainX) > charX:
                    if domainX != domainY and domainX[charX] == domainY[charY]:
                        found = True
            # If it doesnt have a corresponding y, the x domain will be removed
            if not found:
                self.domains[x].remove(domainX)
                revised = True
        return revised

    def ac3(self, arcs=None):
        """
        Update `self.domains` such that each variable is arc consistent.
        If `arcs` is None, begin with initial list of all arcs in the problem.
        Otherwise, use `arcs` as the initial list of arcs to make consistent.

        Return True if arc consistency is enforced and no domains are empty;
        return False if one or more domains end up empty.
        """
        # Check if arcs are given, if not just use the already overlaps
        if arcs == None:
            queue = removeNone(copy.deepcopy(self.crossword.overlaps))
        else:
            queue = arcs

        # A while loop that uses the revise function to remove domains that doesnt give arc consistency
        while queue != {}:
            arc = deQueue(queue)
            if self.revise(arc[0], arc[1]):
                if len(self.domains[arc[0]]) == 0:
                    return False
                # If a change is made in domains, neighboring arcs must be revised again as it may not be consistent anymore
                for z in self.crossword.neighbors(arc[0]):
                    if z == arc[1]:
                        continue
                    else:
                        queue[z, arc[0]] = self.crossword.overlaps[z, arc[0]]
        return True

    def assignment_complete(self, assignment):
        """
        Return True if `assignment` is complete (i.e., assigns a value to each
        crossword variable); return False otherwise.
        """
        # All variables in crossword needs to be assigned, and they need to have a value
        if len(assignment.keys()) == len(self.crossword.variables):
            for key in assignment.keys():
                if assignment[key] != None:
                    continue
                else:
                    return False
            return True
        return False

    def consistent(self, assignment):
        """
        Return True if `assignment` is consistent (i.e., words fit in crossword
        puzzle without conflicting characters); return False otherwise.
        """
        words = set()
        for key in assignment.keys():
            # Check if length of word matches the structure
            if len(assignment[key]) != key.length:
                return False
            # Check if word is distinct
            if assignment[key] in words:
                return False
            # Check for any conflict between neighbors
            for neighbor in self.crossword.neighbors(key):
                if neighbor in assignment:
                    overlap = self.crossword.overlaps[(key, neighbor)]
                    if assignment[key][overlap[0]] != assignment[neighbor][overlap[1]]:
                        return False

            words.add(assignment[key])

        return True


    def order_domain_values(self, var, assignment):
        """
        Return a list of values in the domain of `var`, in order by
        the number of values they rule out for neighboring variables.
        The first value in the list, for example, should be the one
        that rules out the fewest values among the neighbors of `var`.
        """
        order = dict()
        for value in self.domains[var]:
            rulesOut = 0
            for neighbor in self.crossword.neighbors(var):
                if value in self.domains[neighbor]:
                    rulesOut += 1
            order[value] = rulesOut
        order_sorted = list()
        for domain in sorted(order.items(), key=lambda x: x[1], reverse=False):
            order_sorted.append(domain[0])
        return order_sorted


    def select_unassigned_variable(self, assignment):
        """
        Return an unassigned variable not already part of `assignment`.
        Choose the variable with the minimum number of remaining values
        in its domain. If there is a tie, choose the variable with the highest
        degree. If there is a tie, any of the tied variables are acceptable
        return values.
        """
        variables = dict()
        # Check if variable is already assigned, if not check how many values in the domain
        for variable in self.crossword.variables:
            if variable not in assignment:
                variables[variable] = len(self.domains[variable])
        # If there are any variables not assigned - sort them according to their value
        if variables is not None:
            sorted_variables = sorted(variables.items(), key=lambda x: x[1], reverse=False)
            return sorted_variables[0][0]
        else:
            return None


    def backtrack(self, assignment):
        """
        Using Backtracking Search, take as input a partial assignment for the
        crossword and return a complete assignment if possible to do so.

        `assignment` is a mapping from variables (keys) to words (values).

        If no assignment is possible, return None.
        """
        # Check if assignment is complete
        if self.assignment_complete(assignment):
            return assignment

        # Select the a value in the domain for the current variable
        var = self.select_unassigned_variable(assignment)
        for value in self.order_domain_values(var, assignment):
            new_assignment = copy.deepcopy(assignment)
            new_assignment[var] = value
            # Keep track of changes made with the inference and remove the values from the domain
            inferenceValues = list()
            for oldValue in copy.deepcopy(self.domains[var]):
                if oldValue != value:
                    inferenceValues.append(oldValue)
                    self.domains[var].remove(oldValue)
            # Use AC3 to maintain arc consistensy making it more likely for backtrack to choose the right value
            if self.ac3():
                if self.consistent(new_assignment):
                    result = self.backtrack(new_assignment)
                    if result is not None:
                        return result
            # If it didnt work, redo the changes made by the inference
            for oldValue in inferenceValues:
                self.domains[var].add(oldValue)

        return None


def main():

    # Check usage
    if len(sys.argv) not in [3, 4]:
        sys.exit("Usage: python generate.py structure words [output]")

    # Parse command-line arguments
    structure = sys.argv[1]
    words = sys.argv[2]
    output = sys.argv[3] if len(sys.argv) == 4 else None

    # Generate crossword
    crossword = Crossword(structure, words)
    creator = CrosswordCreator(crossword)
    assignment = creator.solve()

    # Print result
    if assignment is None:
        print("No solution.")
    else:
        creator.print(assignment)
        if output:
            creator.save(assignment, output)


if __name__ == "__main__":
    main()
