import numpy as np

class Game:
    mat = None  # this represents the board matrix
    rows = 6                # this represents the number of rows of the board
    cols = 7                # this represents the number of columns of the board
    turn = 1                # this represents whose turn it is (1 for player 1, 2 for player 2)
    wins = 4                # this represents the number of consecutive disks you need to force in order to win


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
    for x, y in np.ndindex(game.mat.shape):
        player = game.mat[x, y]
        if player in (1, 2):
            # check the right n chips
            chain1 = check_chain(game, player, (x, y), (0, 1))
            # check the bottom n chips
            chain2 = check_chain(game, player, (x, y), (1, 0))
            # check the diagonal-top-right n chips
            chain3 = check_chain(game, player, (x, y), (-1, 1))
            # check the diagonal-bottom-right n chips
            chain4 = check_chain(game, player, (x, y), (1, 1))

            if game.wins in (chain1, chain2, chain3, chain4):
                return player

    if 0 in game.mat[0]:  # if the top row has empty slots, there are still valid moves
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


def computer_move(game, level):
    pass


def display_board(game):
    print(game.mat)


def menu():
    my_game = Game()
    my_game.mat = np.zeros((my_game.rows, my_game.cols))

    while check_victory(my_game) == 0:
        display_board(my_game)
        print('Player', my_game.turn, 'turn.')
        col = int(input('Enter column: '))
        while not check_move(my_game, col):
            print('Invalid move.')
            col = int(input('Enter column: '))

        my_game.mat = apply_move(my_game, col)
        my_game.turn ^= 3  # toggles between 1 and 2


if __name__ == "__main__":
    menu()
