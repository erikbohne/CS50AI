import itertools
import random


class Minesweeper():
    """
    Minesweeper game representation
    """

    def __init__(self, height=8, width=8, mines=8):

        # Set initial width, height, and number of mines
        self.height = height
        self.width = width
        self.mines = set()

        # Initialize an empty field with no mines
        self.board = []
        for i in range(self.height):
            row = []
            for j in range(self.width):
                row.append(False)
            self.board.append(row)

        # Add mines randomly
        while len(self.mines) != mines:
            i = random.randrange(height)
            j = random.randrange(width)
            if not self.board[i][j]:
                self.mines.add((i, j))
                self.board[i][j] = True

        # At first, player has found no mines
        self.mines_found = set()

    def print(self):
        """
        Prints a text-based representation
        of where mines are located.
        """
        for i in range(self.height):
            print("--" * self.width + "-")
            for j in range(self.width):
                if self.board[i][j]:
                    print("|X", end="")
                else:
                    print("| ", end="")
            print("|")
        print("--" * self.width + "-")

    def is_mine(self, cell):
        i, j = cell
        return self.board[i][j]

    def nearby_mines(self, cell):
        """
        Returns the number of mines that are
        within one row and column of a given cell,
        not including the cell itself.
        """

        # Keep count of nearby mines
        count = 0

        # Loop over all cells within one row and column
        for i in range(cell[0] - 1, cell[0] + 2):
            for j in range(cell[1] - 1, cell[1] + 2):

                # Ignore the cell itself
                if (i, j) == cell:
                    continue

                # Update count if cell in bounds and is mine
                if 0 <= i < self.height and 0 <= j < self.width:
                    if self.board[i][j]:
                        count += 1

        return count

    def won(self):
        """
        Checks if all mines have been flagged.
        """
        return self.mines_found == self.mines


class Sentence():
    """
    Logical statement about a Minesweeper game
    A sentence consists of a set of board cells,
    and a count of the number of those cells which are mines.
    """

    def __init__(self, cells, count):
        self.cells = set(cells)
        self.count = count

    def __eq__(self, other):
        return self.cells == other.cells and self.count == other.count

    def __str__(self):
        return f"{self.cells} = {self.count}"

    def known_mines(self):
        """
        Returns the set of all cells in self.cells known to be mines.
        """
        # It has to be a mine if number of options equals to number of mines
        if len(self.cells) == self.count and self.count != 0:
            return self.cells
        else:
            return set()

    def known_safes(self):
        """
        Returns the set of all cells in self.cells known to be safe.
        """
        if self.count == 0:
            return self.cells
        else:
            return set()

    def mark_mine(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be a mine.
        """
        if cell in self.cells:
            self.cells.remove(cell)
            self.count -= 1

    def mark_safe(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be safe.
        """
        if cell in self.cells:
            self.cells.remove(cell)


class MinesweeperAI():
    """
    Minesweeper game player
    """

    def __init__(self, height=8, width=8):

        # Set initial height and width
        self.height = height
        self.width = width

        # Keep track of which cells have been clicked on
        self.moves_made = set()

        # Keep track of cells known to be safe or mines
        self.mines = set()
        self.safes = set()

        # List of sentences about the game known to be true
        self.knowledge = []

    def mark_mine(self, cell):
        """
        Marks a cell as a mine, and updates all knowledge
        to mark that cell as a mine as well.
        """
        self.mines.add(cell)
        for sentence in self.knowledge:
            sentence.mark_mine(cell)

    def mark_safe(self, cell):
        """
        Marks a cell as safe, and updates all knowledge
        to mark that cell as safe as well.
        """
        self.safes.add(cell)
        for sentence in self.knowledge:
            sentence.mark_safe(cell)

    def add_knowledge(self, cell, count):
        """
        Called when the Minesweeper board tells us, for a given
        safe cell, how many neighboring cells have mines in them.

        This function should:
            1) mark the cell as a move that has been made
            2) mark the cell as safe
            3) add a new sentence to the AI's knowledge base
               based on the value of `cell` and `count`
            4) mark any additional cells as safe or as mines
               if it can be concluded based on the AI's knowledge base
            5) add any new sentences to the AI's knowledge base
               if they can be inferred from existing knowledge
        """

        # Mark the cell as a move that has been made and as safe
        self.moves_made.add(cell)
        self.mark_safe(cell)

        # Add sentences that are not decided yet to a set for further use
        not_decided_cells = set()
        for i in range(cell[0] - 1, cell[0] + 2):
            for j in range(cell[1] - 1, cell[1] + 2):

                # Do not add the cell itself or if already in safes
                if (i, j) == cell or (i, j) in self.safes:
                    continue

                # If cell is a mine, remove count by 1 and continue
                if (i, j) in self.mines:
                    count -= 1
                    continue

                if inGameboard(i, j):
                    not_decided_cells.add((i, j))

        # Add cells and count to knowledgebase as a new sentence
        self.knowledge.append(Sentence(not_decided_cells, count))

        # Iterate over all knowledge until no new sentences can be made
        newKnowledge = True
        while newKnowledge:
            newKnowledge = False

            # Check for any new safe or mines
            safes, mines = set(), set()

            for sentence in self.knowledge:
                safes = safes.union(sentence.known_safes())
                mines = mines.union(sentence.known_mines())

            # Mark safe if any new safe mines
            if safes:
                newKnowledge = True
                for safe in safes:
                    self.mark_safe(safe)

            # Mark mine if any new mines
            if mines:
                newKnowledge = True
                for mine in mines:
                    self.mark_mine(mine)

            # Delete empty sentences from knowledgebase
            for sentence in self.knowledge:
                if sentence.cells == set():
                    self.knowledge.remove(sentence)

            # Create infrences if possible
            for sentence1 in self.knowledge:
                for sentence2 in self.knowledge:
                    
                    # If it is the same sentence
                    if sentence1 == sentence2:
                        continue
                    
                    # Check if sentence 2 is a subset of sentence 1
                    if sentence2.cells.issubset(sentence1.cells):
                        sentence3 = Sentence(set(), 0)
                        sentence3.cells = sentence1.cells - sentence2.cells
                        sentence3.count = abs(sentence1.count - sentence2.count)
                        
                        # If sentence not already in knowledge - add it to knowledge
                        if sentence3 not in self.knowledge:
                            newKnowledge = True
                            self.knowledge.append(sentence3)
                        

    def make_safe_move(self):
        """
        Returns a safe cell to choose on the Minesweeper board.
        The move must be known to be safe, and not already a move
        that has been made.

        This function may use the knowledge in self.mines, self.safes
        and self.moves_made, but should not modify any of those values.
        """
        for cell in self.safes:
            if cell not in self.moves_made:
                return cell
        return None

    def make_random_move(self):
        """
        Returns a move to make on the Minesweeper board.
        Should choose randomly among cells that:
            1) have not already been chosen, and
            2) are not known to be mines
        """
        # List of all possible moves
        moves = list()
        for i in range(8):
            for j in range(8):
                if (i, j) not in self.moves_made and (i, j) not in self.mines:
                    moves.append((i, j))
        # Return a random move from this list
        if len(moves) == 0:
            return None

        return moves[random.randint(0, len(moves) - 1)]

def inGameboard(x, y):
    """
    Returns True if the cell is in the gameboard
    """
    if x > -1 and x < 8:
        if y > -1 and y < 8:
            return True
    return False