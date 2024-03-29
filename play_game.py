#!/usr/bin/env python3

# # # Imports

import base64
import os
import pickle
import random
import time
import traceback
from datetime import datetime

import chess
import chess.pgn
import chess.svg
import numpy as np
import pandas as pd
import torch
from colorama import Fore, Back, Style, init
from halo import Halo
from termcolor import colored

from basic_state import State

init(autoreset=True)


class Valuator(object):
    def __init__(self):
        from train import Net

        vals = torch.load(
            "neural_nets/value.pth", map_location=lambda storage, loc: storage
        )
        self.model = Net()
        self.model.load_state_dict(vals)

    def __call__(self, s):
        brd = s.serialize()[None]
        output = self.model(torch.tensor(brd).float())
        return float(output.data[0][0])


MAXVAL = 10000


class ClassicValuator(object):
    values = {
        chess.PAWN: 1,
        chess.KNIGHT: 3,
        chess.BISHOP: 3,
        chess.ROOK: 5,
        chess.QUEEN: 9,
        chess.KING: 0,
    }

    def __init__(self):
        self.reset()
        self.memo = {}

    def reset(self):
        self.count = 0

    def __call__(self, s):
        self.count += 1
        key = s.key()
        if key not in self.memo:
            self.memo[key] = self.value(s)
        return self.memo[key]

    def value(self, s):
        b = s.board
        # game over values
        if b.is_game_over():
            if b.result() == "1-0":
                return MAXVAL
            elif b.result() == "0-1":
                return -MAXVAL
            else:
                return 0

        val = 0.0
        # piece values
        pm = s.board.piece_map()
        for x in pm:
            tval = self.values[pm[x].piece_type]
            if pm[x].color == chess.WHITE:
                val += tval
            else:
                val -= tval

        # add a number of legal moves term
        bak = b.turn
        b.turn = chess.WHITE
        val += 0.1 * b.legal_moves.count()
        b.turn = chess.BLACK
        val -= 0.1 * b.legal_moves.count()
        b.turn = bak
        return val


def computer_minimax(s, v, depth, a, b, big=False):
    if depth >= 5 or s.board.is_game_over():
        return v(s)
    # white is maximizing player
    turn = s.board.turn
    if turn == chess.WHITE:
        ret = -MAXVAL
    else:
        ret = MAXVAL
    if big:
        bret = []

    # can prune here with beam search
    isort = []
    for e in s.board.legal_moves:
        s.board.push(e)
        isort.append((v(s), e))
        s.board.pop()
    move = sorted(isort, key=lambda x: x[0], reverse=s.board.turn)

    # beam search beyond depth 3
    if depth >= 3:
        move = move[:10]
    for e in [x[1] for x in move]:
        s.board.push(e)

        tval = computer_minimax(s, v, depth + 1, a, b)
        s.board.pop()
        if big:
            bret.append((tval, e))
        if turn == chess.WHITE:
            ret = max(ret, tval)
            a = max(a, ret)
            if a >= b:
                break  # b cut-off
        else:
            ret = min(ret, tval)
            b = min(b, ret)
            if a >= b:
                break  # a cut-off

    if big:
        return ret, bret
    else:
        return ret


def explore_leaves(s, v):
    spinner = Halo(
        text="SEARCHING STATES",
        text_color="cyan",
        spinner="simpleDotsScrolling",
        color="cyan",
    )
    spinner.start()
    start = time.time()
    v.reset()
    bval = v(s)
    try:
        cval, ret = computer_minimax(s, v, 0, a=-MAXVAL, b=MAXVAL, big=True)
    except:
        cval = 0
        ret = []
    eta = time.time() - start
    spinner.stop()
    print(
        colored(
            Style.BRIGHT + "%.2f -> %.2f: explored %d nodes in %.3f seconds %d/sec",
            "yellow",
        )
        % (bval, cval, v.count, eta, int(v.count / eta))
    )
    return ret


# chess board and "engine"
s = State()
# v = Valuator()
v = ClassicValuator()


def to_svg(s):
    return base64.b64encode(chess.svg.board(board=s.board).encode("utf-8")).decode(
        "utf-8"
    )


from flask import Flask, request

app = Flask(__name__)

winners = np.array([])


@app.route("/")
def hello():
    ret = open("index.html").read()
    return ret.replace("start", s.board.fen())


def computer_move(s, v):
    # computer move
    try:
        move = sorted(explore_leaves(s, v), key=lambda x: x[0], reverse=s.board.turn)
    except:
        move = []
    if len(move) == 0:
        m1 = "game over"
        return m1
    print(colored(Style.BRIGHT + "top 3:", "green"))
    for i, m in enumerate(move[0:3]):
        mi = str(m)
        m1 = mi.split(
            "(",
        )[1]
        m2 = m1.split(
            ",",
        )[0]
        m = mi.split(
            "'",
        )[1]
        print(
            "  ",
            colored(Style.DIM + "Value increase: ", "green"),
            colored(Style.BRIGHT + m2, "cyan"),
            colored(Style.DIM + " for move ", "green"),
            colored(Style.BRIGHT + m, "cyan"),
        )
        if s.board.turn == False:
            comp = colored(Back.WHITE + Fore.BLACK + Style.DIM + "Human/White")
        else:
            comp = colored(Back.MAGENTA + Fore.CYAN + Style.BRIGHT + "Computer")
    # readout = str(comp, colored(Style.BRIGHT + "moving",'magenta'), colored(Style.BRIGHT + str(move[0][1]),'yellow'))
    print(
        comp,
        colored(Style.BRIGHT + "moving", "magenta"),
        colored(Style.BRIGHT + str(move[0][1]), "yellow"),
    )
    s.board.push(move[0][1])
    m1 = str(move[0][1])
    # game = chess.pgn.Game()
    return m1, s


i = 0
with open("data_pickles/rnd.pickle", "wb") as rnd:
    pickle.dump(i, rnd)
moves = []
with open("data_pickles/g.pickle", "wb") as g:
    pickle.dump(moves, g)


@app.route("/selfplay")
def selfplay():
    m = request.args.get("m", default="")
    try:
        with open("data_pickles/rnd.pickle", "rb") as rnd:
            i = pickle.load(rnd)
            i = 1 + i
    except:
        i = 0
    with open("data_pickles/rnd.pickle", "wb") as rnd:
        pickle.dump(i, rnd)
    if m == "":
        # print('got1')
        s = State()
        # s = request.args.get('s', default='')
        ret = "game over"
        while not s.board.is_game_over():
            while not s.board.is_stalemate():
                print(colored("move: " + str(i), "yellow"))
                print(colored(m, "cyan"))
                # ORIGINAL with added state reply m2,si = computer_move(s, v)
                # Added random pawn move
                vector = ["a", "b", "c", "d", "e", "f", "g", "h"]
                sauce = random.choice(vector)
                # only moving straight
                # add 2 step first move
                vector1 = [3, 4]
                tustep = str(random.choice(vector1))
                rndmove = sauce + str(2) + sauce + tustep
                s.board.push_san(rndmove)
                with open("data_pickles/si.pickle", "wb") as p:
                    pickle.dump(s, p)
                with open("data_pickles/g.pickle", "rb") as g:
                    moves = pickle.load(g)
                    moves.append(rndmove)
                with open("data_pickles/g.pickle", "wb") as g:
                    pickle.dump(moves, g)
                    print(colored(moves, "cyan"))
                m1 = rndmove + ":"
                response = app.response_class(response=m1 + s.board.fen(), status=200)
                return response
            m1 = "stalemate:"
            response = app.response_class(response=m1 + s.board.fen(), status=200)
            return response
        return ret
    else:
        ret = "game over"
        with open("data_pickles/si.pickle", "rb") as f:
            si = pickle.load(f)
        while not si.board.is_game_over():
            while not si.board.is_stalemate():
                m2, sii = computer_move(si, v)
                with open("data_pickles/si.pickle", "wb") as p:
                    pickle.dump(sii, p)
                print(colored("move: " + str(i), "yellow"))
                with open("data_pickles/g.pickle", "rb") as g:
                    moves = pickle.load(g)
                    moves.append(m2)
                with open("data_pickles/g.pickle", "wb") as g:
                    pickle.dump(moves, g)
                    print(colored(moves, "cyan"))
                m1 = m2 + ":"
                response = app.response_class(response=m1 + si.board.fen(), status=200)
                return response
            m1 = "stalemate:"
            resp = app.response_class(response=m1 + si.board.fen(), status=200)
            return resp
        return ret


# moves given as coordinates of piece moved
@app.route("/move_coordinates")
def move_coordinates():
    with open("data_pickles/rnd.pickle", "rb") as rnd:
        i = pickle.load(rnd)
        i = 1 + i
    with open("data_pickles/rnd.pickle", "wb") as rnd:
        pickle.dump(i, rnd)
    print(colored("move: " + str(i), "yellow"))
    if not s.board.is_game_over():
        source = int(request.args.get("from", default=""))
        sauce = request.args.get("sauce", default="")
        try:
            target = int(request.args.get("to", default=""))
        except:
            m1 = ":"
            response = app.response_class(response=m1 + s.board.fen(), status=200)
            return response
        targe = request.args.get("targe", default="")
        promotion = (
            True if request.args.get("promotion", default="") == "true" else False
        )
        move = s.board.san(
            chess.Move(source, target, promotion=chess.QUEEN if promotion else None)
        )
        if move is not None and move != "":
            print(
                colored(Style.BRIGHT + "human moves", "cyan"),
                colored(Style.BRIGHT + move, "green"),
            )
            m1 = ":"
            move1 = sauce + targe
            try:
                s.board.push_san(move)
                with open("data_pickles/g.pickle", "rb") as g:
                    moves = pickle.load(g)
                    moves.append(move1)
                with open("data_pickles/g.pickle", "wb") as g:
                    pickle.dump(moves, g)
                    print(colored(moves, "cyan"))
                m2, s1 = computer_move(s, v)
                with open("data_pickles/g.pickle", "rb") as g:
                    moves = pickle.load(g)
                    moves.append(m2)
                with open("data_pickles/g.pickle", "wb") as g:
                    pickle.dump(moves, g)
                    print(colored(moves, "cyan"))
                m1 = m2 + ":"
            except Exception:
                traceback.print_exc()
            response = app.response_class(response=m1 + s.board.fen(), status=200)
        return response
    print(
        colored(
            Style.BRIGHT + "********************* GAME IS OVER *********************",
            "red",
        )
    )
    response = app.response_class(response="game over", status=200)
    return response


wins = pd.DataFrame({"W": [1, 0], "B": [0, 1], "Winner": ["White", "Black"]})
with open("data_pickles/w.pickle", "wb") as w:
    pickle.dump(wins, w)


@app.route("/post")
def post():
    game = chess.pgn.Game()
    game.headers["Event"] = "Game"
    game.headers["Site"] = "local"
    game.headers["Date"] = str(datetime.now())
    game.headers["White"] = "Human/White"
    game.headers["Black"] = "Computer/Black"
    with open("data_pickles/si.pickle", "rb") as f:
        si = pickle.load(f)
        b = si.board
        # game over values
        if b.result() == "1-0":
            game.headers["Result"] = "1-0"
            winner = "WHITE"
        elif b.result() == "0-1":
            game.headers["Result"] = "0-1"
            winner = "BLACK"
        else:
            winner = "BLACK"
        win = open("winner.txt", "a")
        game.end()
        print(game)
        with open("data_pickles/g.pickle", "rb") as g:
            moves = pickle.load(g)
            movesst = str(moves)
            print(colored("Game Final", "cyan") + movesst)
        node = game.add_variation(chess.Move.from_uci(moves[0]))
        for m in moves:
            node = node.add_variation(chess.Move.from_uci(m))
        stamp = str(datetime.now()).replace(":", "_")
        log = open("training_games/" + stamp + ".pgn", "w+")
        try:
            sgame = "Final Board:\n" + str(movesst)
        except:
            print(colored(Style.BRIGHT + "Save Game Fail", "red"))
        log.write(sgame)
        win.write(winner + ":\n" + sgame)
        if winner == "BLACK":
            res1 = 0
            res2 = 1
        else:
            res1 = 1
            res2 = 0
    with open("data_pickles/w.pickle", "rb") as w:
        wins = pickle.load(w)
    win1 = pd.DataFrame({"W": [res1], "B": [res2], "Winner": [winner]})
    pd.DataFrame.append(wins, win1)
    with open("data_pickles/w.pickle", "wb") as w:
        pickle.dump(wins, w)
    html = wins.to_html()
    response = app.response_class(response=html, status=200)
    i = 0
    with open("data_pickles/rnd.pickle", "wb") as rnd:
        pickle.dump(i, rnd)
    with open("data_pickles/g.pickle", "wb") as g:
        moves = []
        pickle.dump(moves, g)
    return response


@app.route("/new_game")
def new_game():
    s.board.reset()
    response = app.response_class(response=s.board.fen(), status=200)
    i = 0
    with open("data_pickles/rnd.pickle", "wb") as rnd:
        pickle.dump(i, rnd)
    with open("data_pickles/g.pickle", "wb") as g:
        moves = []
        pickle.dump(moves, g)
    return response


@app.route("/undo")
def undo():
    s.board.pop()
    response = app.response_class(response=s.board.fen(), status=200)
    return response


if __name__ == "__main__":
    if os.getenv("SELFPLAY") is not None:
        s = State()
        print(s.board)
        print(s.board.result())
    else:
        app.run(debug=True)
