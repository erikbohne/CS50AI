from tictactoe import player, odd, actions, result, winner, terminal, full, minimax, min_val, max_val
EMPTY = None
X = "X"
O = "O"

board = [[O, EMPTY, EMPTY],
        [EMPTY, X, EMPTY],
        [EMPTY, EMPTY, EMPTY]]

#print(player(board))
#print(actions(board))
# print(result(board, (2,2)))
#print(winner(board))
#print(terminal(board))
minimax(board)