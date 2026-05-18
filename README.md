# monkish: v1.0.0 🦍🦍🦍

a bitboard-based chess engine with a neural network evaluator, written in
Python.

**strength: 800-1100 ELO (not tested formally)**

## try it out!

```bash
# play against the engine
python3 -m main pve

# watch the engine play itself
python3 -m main eve

# custom depth or model
python3 -m main pve --depth 4
python3 -m main eve --model alpha_10mil --depth 5

# check out perft tests
python3 -m tests.perft_test

# validate the neural evaluator
python3 -m tests.neural_test
```

## architecture

**move gen** : _validated with perft testing across standard positions_

- bitboard representation
- ray attacks + lookup tables for knights and kings
- full pawn logic (double pushes, en passant, promotions)
- check detection and pseudo-legal move filtering

**neural eval** :

- 6-layer CNN trained on 10M Stockfish-annotated positions (PyTorch, MPS)
- Pearson correlation 0.810 on held-out positions

**search** :

- alpha-beta minimax with a hybrid eval: 70% neural + 30% basic material score
- eval is tanh-normalized to [-1, 1], positive->white's winning
- default depth of 3 (can be changed)

## todos

- [ ] quiescence search (variable depth)
- [ ] improved eval (weighted loss retraining, PST)
- [ ] C rewrite
- [ ] NNUE?

## results

| metric              | val    |
| ------------------- | ------ |
| MAE                 | 0.2259 |
| R^2                 | 0.6430 |
| pearson correlation | 0.8099 |

breakdown by eval zone:

_it has general biases in equal positions, blindness in complete winning
positions._

| zone         | MAE    | bias    |
| ------------ | ------ | ------- |
| -1.0 to -0.5 | 0.3907 | +0.3854 |
| -0.5 to 0.0  | 0.1749 | +0.1278 |
| 0.0 to +0.5  | 0.1430 | -0.0261 |
| +0.5 to +1.0 | 0.3289 | -0.3200 |

## notes & known issues

_these are qualitative notes from testing._

the model plays decently, with some multi-move tactics and positional knowledge.
it falters in the opening: blunders small material and makes more passive moves.
its strongest in the middlegame, playing well when converting a middlegame
advantage but struggles in pure endgames when eval saturates, especially in
losing positions.

limitations include the python framework the engine is based on, its biases from
the training process, and lack of depth (too slow). played best moves are more
accurate rather than the actual positional evals themselves. on top of that,
evaluations for endgames in clearly winning positions confuse the engine, not
enough differentiation with tanh-normalization.

currently stops game when it clearly will be checkmated (M1) rather than play
through checkmate (needs to be fixed).
