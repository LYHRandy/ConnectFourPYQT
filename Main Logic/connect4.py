import numpy as np

from random import randint
from copy import deepcopy

class Game:
    mat = None  # this represents the board matrix
    rows = 6                # this represents the number of rows of the board
    cols = 7                # this represents the number of columns of the board
    turn = 1                # this represents whose turn it is (1 for player 1, 2 for player 2)
    wins = 4                # this represents the number of consecutive disks you need to force in order to win


def longest_chain(game, turn):
    result = 0
    for x, y in np.ndindex(game.mat.shape):
        if game.mat[x, y] == turn:
            # check the right n chips
            chain1 = check_chain(game, turn, (x, y), (0, 1))
            # check the bottom n chips
            chain2 = check_chain(game, turn, (x, y), (1, 0))
            # check the diagonal-top-right n chips
            chain3 = check_chain(game, turn, (x, y), (-1, 1))
            # check the diagonal-bottom-right n chips
            chain4 = check_chain(game, turn, (x, y), (1, 1))

            result = max(result, chain1, chain2, chain3, chain4)
    return result


def check_chain(game, player, coords, move_coords, chain=0):
    x, y = coords
    move_x, move_y = move_coords

    # if the current chip is the winning chip or if out of bounds or if the current chip is not the player's
    if chain == game.wins or (x > game.rows - 1 or y > game.cols - 1) or game.mat[x, y] != player:
        return chain

    # move on to the next chip in the chain
    new_x, new_y = (x + move_x), (y + move_y)
    return check_chain(game, player, (new_x, new_y), (move_x, move_y), chain + 1)


def check_victory(game):
    '''
    0 is no winning/draw situation is present for this game
    1 if player 1 wins
    2 if player 2 wins
    3 if it is a draw
    '''
    # look for player victory
    if game.wins == longest_chain(game, game.turn):
        return game.turn
    elif 0 in game.mat[0]:  # if the top row has empty slots, there are still valid moves
        return 0
    else:  # else it's a draw
        return 3


def apply_move(game, col, pop=False):
    board = game.mat.copy()
    row = board[:, col][::-1].tolist().index(0)
    board[game.rows - row - 1, col] = game.turn
    return board


def check_move(game, col, pop=False):
    can_pop = pop and game.mat[-1, col] == game.turn
    return game.mat[0, col] == 0 or can_pop


def computer_move(game, level=3):
    best_move = randint(0, game.cols - 1)
    orig_board = game.mat.copy()
    if level == 2:
        for i in range(game.cols):
            if check_move(game, i):
                game.mat = apply_move(game, i)
                if check_victory(game) == 2:
                    best_move = i
                    break
    if level == 3:
        best_score = 0
        for i in range(game.cols):
            if check_move(game, i):
                game.mat = apply_move(game, i)
                current_score = minimax(game)
                if current_score == -game.wins:  # Ai is about to lose
                    best_move = i
                    break
                elif current_score > best_score:
                    best_score = current_score
                    best_move = i
    game.mat = orig_board
    return best_move


def display_board(game):
    print(game.mat)


def menu():
    my_game = Game()
    my_game.mat = np.zeros((my_game.rows, my_game.cols))
    my_game.mat[-3:, randint(0, my_game.cols - 1)] = 2

    level = input('AI Level (1/2/3): ')
    while level not in ('1', '2', '3'):
        level = input('AI Level (1/2/3): ')
    level = int(level)
    print('AI is running at level', level)

    while True:
        display_board(my_game)
        print('Player', my_game.turn, 'turn.')
        if my_game.turn == 1:
            col = int(input('Enter column: '))
        else:
            col = computer_move(my_game, level=level)

        while not check_move(my_game, col):
            print('Invalid move.')
            col = int(input('Enter column: '))

        my_game.mat = apply_move(my_game, col)
        if check_victory(my_game) != 0:
            break
        my_game.turn ^= 3  # toggles between 1 and 2
    display_board(my_game)


def minimax(game, depth=4, alpha=-1_000_000, beta=1_000_000, is_max=True):
    outcome = check_victory(game)
    if depth == 0 or outcome == 3:
        return longest_chain(game, 2) # return static evaluation of position
    elif outcome == 2:  # or game is won by AI
        return game.wins
    elif outcome == 1:  # or game is won by player
        return -game.wins

    if is_max:
        max_eval = -1_000_000
        for i in range(game.cols):
            if check_move(game, i):
                new_game = deepcopy(game)
                new_game.turn = 2  # AI is the maximising player
                new_game.mat = apply_move(new_game, i)
                eval = minimax(new_game, depth - 1, alpha, beta, False)
                max_eval = max(max_eval, eval)
                alpha = max(alpha, eval)
                if beta <= alpha:
                    break
        return max_eval
    else:
        min_eval = 1_000_000
        for i in range(game.cols):
            if check_move(game, i):
                new_game = deepcopy(game)
                new_game.turn = 1  # Player is the minimising player
                new_game.mat = apply_move(new_game, i)
                eval = minimax(new_game, depth - 1, alpha, beta, True)
                min_eval = min(min_eval, eval)
                beta = min(beta, eval)
                if beta <= alpha:
                    break
        return min_eval


if __name__ == "__main__":
    menu()
