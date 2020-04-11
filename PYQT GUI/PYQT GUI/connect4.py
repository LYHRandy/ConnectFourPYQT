from copy import deepcopy
from random import randint, choice
import os

import numpy as np
from numpy.core.numeric import False_


class Game:
    mat = None  # this represents the board matrix
    rows = 6                # this represents the number of rows of the board
    cols = 7                # this represents the number of columns of the board
    turn = 1                # this represents whose turn it is (1 for player 1, 2 for player 2)
    wins = 4                # this represents the number of consecutive disks you need to force in order to win
    game_state = None 

def longest_chain(game, turn):
    result = 0
    for x, y in np.ndindex(game.mat.shape):
        if game.mat[x, y] == turn:
            # check the right n chips
            chain1 = check_chain(game, turn, (x, y), (0, 1))
            # check the bottom n chips
            chain2 = check_chain(game, turn, (x, y), (1, 0))
            # check the diagonal-top-right n chips
            chain3 = check_chain(game, turn, (x, y), (1, -1))
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


def check_victory(game,mode="player"):
    '''
    0 is no winning/draw situation is present for this game
    1 if player 1 wins
    2 if player 2 wins
    3 if it is a draw
    '''
    # look for player victory
    chain = longest_chain(game,game.turn)
    filename = "state-" + mode + ".txt" 
    if game.wins == chain:
        if os.path.exists(filename):
            os.remove(filename)
        return game.turn
    elif 0 in game.mat[0]:  # if the top row has empty slots, there are still valid moves
        return 0
    else:  # else it's a draw
        return 3


def apply_move(game, col,mode="player"):
    board = game.mat.copy()
    row = board[:, col][::-1].tolist().index(0)
    board[game.rows - row - 1, col] = game.turn

    # whenever apply move is called, save game state
    filename = "state-" + mode + ".txt" 
    with open(filename,"w") as f:
        for row in board:
            for cell_idx in range(len(row)-1):
                print(str(row[cell_idx]),end='|',file=f)
            f.write(str(row[-1]))
            f.write("\n")
        # store the next player' turn instead. so when load state, it rmbs is the other player's turn
        player_turn = game.turn ^ 3
        f.write(str(player_turn))
        
    return board


def check_move(game, col):
    
    return game.mat[0, col] == 0

def check_player_winning(game,i):
    #Check the score of player 1
    player_score = longest_chain(game,1)
    to_block = False
    move_to_block = None
    if player_score == 3:
        for x, y in np.ndindex(game.mat.shape):
            if game.mat[x, y] == 1:
                # check the right n chips
                chain1 = check_chain(game, 1, (x, y), (0, 1))
                if chain1 == 3:
                    # your either block in front of behind so is y-1 or y+3
                    move_to_block = y+3
                    if move_to_block < game.cols and game.mat[x,move_to_block]!=2 and game.mat[x,move_to_block]!=0:
                        to_block = True
                        break
                    move_to_block = y-1
                    if move_to_block >= 0 and game.mat[x,move_to_block]!=2 and game.mat[x,move_to_block]!=0:
                        to_block = True
                        break
                    move_to_block = None
                # check the bottom n chips
                chain2 = check_chain(game, 1, (x, y), (1, 0))
                if chain2 == 3 and check_move(game,y):
                    to_block = True
                    move_to_block = y
                    break
                # check the diagonal-top-right n chips
                chain3 = check_chain(game, 1, (x, y), (1, -1))
                if chain3 == 3:
                    move_to_block = y + 1
                    if move_to_block < game.cols and game.mat[x,move_to_block]!=0:
                        to_block = True
                        break

    return to_block, move_to_block

def computer_move(game,player_move, level=3):
    best_move = randint(0, game.cols - 1)
    if level == 2:
        turn_player = game.turn
        for i in range(game.cols):
            if check_move(game,i):
                orig_board = game.mat.copy()
                game.mat = apply_move(game, i)
                if player_move:
                    #Check if AI has a chance to win
                    if check_victory(game)==2:
                        best_move = i
                        break
                    if player_move== 0:
                        best_move = randint(player_move,player_move+1)
                        if player_move + 1 >= game.cols:
                            best_move = player_move
                    else:
                        min_value = player_move -1 
                        max_value = player_move + 1
                        best_move = randint(min_value,max_value)
                        if player_move -1 < 0:
                            min_value = 0
                        if player_move + 1 >= game.cols:
                            max_value = player_move
                        best_move = randint(min_value,max_value)
                game.mat = orig_board
        game.turn = turn_player
        game.mat = orig_board
            

    if level == 3:
        turn_player = game.turn
        for i in range(game.cols):
            if check_move(game, i):
                orig_board = game.mat.copy()
                game.mat = apply_move(game, i)
                to_block, move_to_block = check_player_winning(game,i)
                if to_block and move_to_block:
                    best_move = move_to_block
                    break
                game.mat = orig_board
                game.turn ^= 3
                game.mat = apply_move(game, i)
                if check_victory(game) == 1:  # AI is about to lose
                    best_move = i
                    break
                if player_move:
                    #Check if AI has a chance to win
                    if check_victory(game)==2:
                        best_move = i
                        break
                    if player_move== 0:
                        best_move = randint(player_move,player_move+1)
                        if player_move + 1 >= game.cols:
                            best_move = player_move
                    else:
                        min_value = player_move -1 
                        max_value = player_move + 1
                        best_move = randint(min_value,max_value)
                        if player_move -1 < 0:
                            min_value = 0
                        if player_move + 1 >= game.cols:
                            max_value = player_move
                        best_move = randint(min_value,max_value)
                game.mat = orig_board
        game.turn = turn_player
        game.mat = orig_board

    if level == 4:
        best_score = 0
        for i in range(game.cols):
            if check_move(game, i):
                orig_board = game.mat.copy()
                game.mat = apply_move(game, i)
                current_score = minimax(game)
                game.mat = orig_board
                if current_score == -game.wins:  # Ai is about to lose
                    best_move = i
                    break
                elif current_score > best_score:
                    best_score = current_score
                    best_move = i
        game.mat = orig_board

    available_cols = []
    board = game.mat.copy()
    for j in range(game.cols):
        try:
            row = board[:,j].tolist().index(0)
            if game.rows-row-1 > 0:
                available_cols.append(j)
        except:
            continue
        
    if best_move not in available_cols:
        best_move = choice(available_cols)

    return best_move


def display_board(game):
    print(game.mat)


def menu():
    my_game = Game()
    my_game.mat = np.zeros((my_game.rows, my_game.cols))
    #my_game.mat[-3:, randint(0, my_game.cols - 1)] = 2

    level = input('AI Level (1/2/3): ')
    while level not in ('1', '2', '3'):
        level = input('AI Level (1/2/3): ')
    level = int(level)
    print('AI is running at level', level)
    player_move = 0

    while True:
        display_board(my_game)
        print('Player', my_game.turn, 'turn.')
        if my_game.turn == 1:
            col = int(input('Enter column: '))
            player_move = col
        else:
            col = computer_move(my_game,player_move=player_move, level=level)
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
