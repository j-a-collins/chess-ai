# Training a toy Neural Net to play chess

Having recently been reading [Deep Thinking](https://www.goodreads.com/book/show/31934455-deep-thinking) by Garry Kasparov; this program
will aim to explore some of the ideas he defines as Type A and Type B chess
programs which I thought were interesting to think about - type A being brute force, type B being intelligent choice of move. The main aim here is to:

1. Formulate a tree data structure for move-searching, and;
2. Utilise a NN to collapse the search tree formulated in (1) based on
historical games from a database of PGN chess games (from https://database.lichess.org).

This model uses the [python-chess](https://python-chess.readthedocs.io) library, which is an excellent resource, recommended highly.

Current state: in progress.

Other cool stuff discussed on the way to completing this project:
* The [Shannon number](https://en.wikipedia.org/wiki/Shannon_number)
* The [oldest](https://www.chess2u.com/t8826-oldest-recorded-chess-game) notated game of chess
* The possibility of training the NN from all the recorded games of a [single chess master](https://www.chessgames.com/perl/chessplayer?pid=15940)

