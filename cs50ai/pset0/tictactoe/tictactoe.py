"""
Tic Tac Toe Player
"""

import math
import copy

X = "X"
O = "O"
EMPTY = None
INFINITY = math.inf


def initial_state():
    """
    Returns starting state of the board.
    """
    return [[EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY]]


def player(board):
    """
    Returns player who has the next turn on a board.
    """
    turns = 0
    for i in range(3):
        for j in range(3):
            if board[i][j] != EMPTY:
                turns += 1
    if odd(turns):
        return O
    else:
        return X


def actions(board):
    """
    Returns set of all possible actions (i, j) available on the board.
    """
    actions = []
    for i in range(3):
        for j in range(3):
            if board[i][j] == EMPTY:
                actions.append((i,j))
    return actions


def result(board, action):
    """
    Returns the board that results from making move (i, j) on the board.
    """
    new_board = copy.deepcopy(board)

    # Check if move is valid
    if new_board[action[0]][action[1]] != EMPTY:
        raise NameError('Invalid move')

    # Create new board with the move
    new_board[action[0]][action[1]] = player(board)

    return new_board


def winner(board):
    """
    Returns the winner of the game, if there is one.
    """
    curr = EMPTY

    # Check horisontal rows
    for i in range(3):
        if board[i][0] != EMPTY:
            curr = board[i][0]
        for j in range(3):
            if board[i][j] != curr:
                break
            if j == 2:
                return curr

    # Check vertical rows
    j = 0
    for i in range(3):
        if board[j][i] != EMPTY:
            curr = board[j][i]
        for j in range(3):
            if board[j][i] != curr:
                break
            if j == 2:
                return curr

    # Check diagonal rows
    curr = board[0][0]
    for i in range(1, 3):
        if board[i][i] != curr:
            break
        if i == 2:
            return curr
    curr = board[0][2]
    for i in range(1, 3):
        if board[i][2 - i] != curr:
            break
        if i == 2:
            return curr

    return None


def terminal(board):
    """
    Returns True if game is over, False otherwise.
    """
    if winner(board) != None:
        return True
    elif full(board):
        return True
    else:
        return False


def utility(board):
    """
    Returns 1 if X has won the game, -1 if O has won, 0 otherwise.
    """
    if winner(board) == X:
        return 1
    elif winner(board) == O:
        return -1
    else:
        return 0


def minimax(board):
    """
    Returns the optimal action for the current player on the board.
    """
    if terminal(board):
        return None
    elif board == initial_state():
        return (0,0)

    if player(board) == X:
        maxVal = -INFINITY
        for action in actions(board):
            if maxVal < max(maxVal, min_val(result(board, action))):
                maxVal = min_val(result(board, action))
                bestAction = action
    else:
        minVal = INFINITY
        for action in actions(board):
            if minVal > min(minVal, max_val(result(board, action))):
                minVal = max_val(result(board, action))
                bestAction = action
    return bestAction

def odd(number):
    """
    Returns True if number is even.
    """
    if number % 2 != 0 and number > 0:
        return True
    else:
        return False


def full(board):
    """
    Returns True if board is full.
    """
    for i in range(3):
        for j in range(3):
            if board[i][j] == EMPTY:
                return False
    return True


def min_val(board):
    """
    Returns min value of a path.
    """
    if terminal(board):
        return utility(board)

    minvalue = INFINITY
    for action in actions(board):
        if minvalue != min(minvalue, max_val(result(board, action))):
            minvalue = max_val(result(board, action))
    return minvalue


def max_val(board):
    """
    Returns max value of a path.
    """
    if terminal(board):
        return utility(board)

    maxvalue = -INFINITY
    for action in actions(board):
        if maxvalue != max(maxvalue, min_val(result(board, action))):
            maxvalue = min_val(result(board, action))
    return maxvalue