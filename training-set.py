#!/usr/bin/env python3

'''
Training model using PNG data from database.lichess.org

Last write
user: j-a-collins
date: 06-02-21
'''

# # # imports
import chess.pgn
import os
from basic_state import State

pgn = open("lichess-PGNs\\kasparov_deep_blue_1996.pgn")
game = chess.pgn.read_game(pgn)
game.headers["Event"]
points = {'1/2-1/2':0, '1-0':1, '0-1':-1}[game.headers['Result']]
board = game.board()
for i, move in enumerate(game.mainline_moves()):
    board.push(move)
    # print("#" + str(i) + ": " + str(move))
    print(points, State(board).serialise())
    print('\n')
print('game over')

