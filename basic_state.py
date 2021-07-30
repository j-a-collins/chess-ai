#!/usr/bin/env python3

'''
Main class for chess board state

Last write
user: j-a-collins
date: 08-02-21
'''

# # # imports
import chess
import numpy as np


class State(object):
    def __init__(self, board=None):
        if board is None:
            self.board = chess.Board()
        else:
            self.board = board

    def key(self):
        return (self.board.board_fen(), self.board.turn, self.board.castling_rights, self.board.ep_square)

    def serialise(self):
        '''
        Function to validate the
        state of the board.
        '''
        assert self.board.is_valid()
        board_state = np.zeros(64, np.uint8)
        for i in range(64):
            piece_position = self.board.piece_at(i)
            if piece_position is not None:
                print(i, piece_position.symbol())
                board_state[i] = {'P': 1, 'N': 2, 'B': 3, 'R': 4, 'Q': 5, 'K': 6, \
                            'p': 9, 'n':10, 'b':11, 'r':12, 'q':13, 'k':14}[piece_position.symbol()]

        # # # Logic for handling castling rights # # #
        if self.board.has_queenside_castling_rights(chess.WHITE):
            assert board_state[0] == 4
            board_state[0] = 7

        if self.board.has_kingside_castling_rights(chess.WHITE):
            assert board_state[7] == 4
            board_state[7] = 7

        if self.board.has_queenside_castling_rights(chess.BLACK):
            assert board_state[56] == 12 # 8 + 4 
            board_state[56] = 8 + 7

        if self.board.has_kingside_castling_rights(chess.BLACK):
            assert board_state[63] == 12 # 8 + 4
            board_state[63] = 15 # 8 + 7

        # # # Logic for handling en passant # # #
        if self.board.ep_square is not None:
            assert board_state[self.board.ep_square] == 0
            board_state[self.board.ep_square] = 8
        board_state = board_state.reshape(8, 8)

        # # # For conversion to binary - returns 257 bits
        binary_state = np.zeros((5, 8, 8), np.uint8)

        binary_state[0] = (board_state>>3) & 1
        binary_state[1] = (board_state>>2) & 1
        binary_state[2] = (board_state>>1) & 1
        binary_state[3] = (board_state>>0) & 1
        # # # The final column indicates white or black's turn
        binary_state[4] = (self.board.turn * 1.0)
        return binary_state

    
    def edges(self):
        '''
        Returns a dynamic list of legal moves
        as a list.
        '''
        return list(self.board.legal_moves)


if __name__ == "__main__":
    s = State()
    print(s.serialise())
