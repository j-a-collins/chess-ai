#!/usr/bin/env python3

import chess

class State(object):
    def __init__(self):
        self.board = chess.Board()


    def serialise(self):
        # # # 257 bits - look into this
        pass


    def edges(self):
        return list(self.board.legal_moves)


    def value(self):
        # TO-DO: Neural net at this stage
        return 1 # all board positions are equal


if __name__ == "__main__":
    s = State()
    print(s.edges())

