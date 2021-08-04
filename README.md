# Training a Toy Neural Net to Play Chess

Having recently finished reading [Deep Thinking](https://www.goodreads.com/book/show/31934455-deep-thinking) by Garry Kasparov; this program
will aim to explore some of the ideas he defines as Type A and Type B chess
programs which I thought were interesting to think about - type A being a brute force approach, type B being an approach focused on an intelligent choice of move. The main aim here is to:

1. Formulate a tree data structure for move-searching, and;
2. Utilise a NN to collapse the search tree formulated in (1) based on
historical games from a database of PGN chess games (which I've taken from https://database.lichess.org).

This model uses the [python-chess](https://python-chess.readthedocs.io) library, which is an excellent resource for any similar projects, recommended highly. I also use [PyTorch](https://pypi.org/project/torch/) for the neural network. PyTorch is killer, use it!

Current state: In progress. Logging added, some colour schemas, design needs to be finished then the model could possibly deployed properly. Some minor bug fixes to come, any help is welcome.

Other cool stuff discussed on the way to completing this project:
* The [Shannon number](https://en.wikipedia.org/wiki/Shannon_number)
* The [oldest](https://www.chess2u.com/t8826-oldest-recorded-chess-game) notated game of chess
* The possibility of training the NN from all the recorded games of a [single chess master](https://www.chessgames.com/perl/chessplayer?pid=15940)

Install/Run
-----

```
 pull down the repo
 # Install dependencies:
 pip install torch torchvision numpy flask python-chess termcolor halo pickle
 # Then run it:
 python play_game.py   # Flask opens on http://127.0.0.1:5000/
```

<img width=400px src="https://raw.githubusercontent.com/j-a-collins/chess-ai/master/static/img/screenshot/neural-net-chess-img.JPG" />

