#!/usr/bin/env python3

'''
Training model using PNG data from database.lichess.org
processes

Last write
user: j-a-collins
date: 08-02-21
'''

# # # imports
import chess.pgn
from basic_state import State
import os
import numpy as np


def get_training_data(number_of_samples = None):
    '''
    A function to get all the PGNs from a specified folder
    and analyse the data for points values and then process
    them. It then returns two arrays.
    '''
    x, y = [], []
    game_notation = 0
    points = {'1/2-1/2':0, '0-1':-1, '1-0':1}

    # PGN data files sit inside the lichess-PGNs folder
    # May be better to use glob?
    directory = 'C:\\Users\\jacka\\Documents\\chess-ai-master\\chess-ai-master\\lichess-PGNs'
    for file_name in os.listdir(directory):
        pgn = open(os.path.join(directory, file_name))
        while True:
            game = chess.pgn.read_game(pgn)
            if game is None:
                break
            result_of_game = game.headers['Result']
            if result_of_game not in points:
                continue

            point_value = points[result_of_game]
            board = game.board()

            # Mainline_moves: iterates over the main moves and plays them on a board
            for i, move in enumerate(game.mainline_moves()):
                board.push(move)
                arrange_in_series = State(board).serialise()
                x.append(arrange_in_series)
                y.append(point_value)

            print(f"Processing {game_notation}. Contains {len(x)} examples.")

            if number_of_samples is not None and len(x) > number_of_samples:
                return x, y
            game_notation += 1
    x = np.array(x)
    y = np.array(y)

    return x, y

if __name__ == "__main__":
    NUMBER_OF_PGNS = 25000000 # Currently hardcoded the number of PGNs
    x, y = get_training_data(NUMBER_OF_PGNS)
    # Saves the arrays into an uncompressed .npz
    np.savez("processed/dataset.npz", x, y)
