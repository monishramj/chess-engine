# from board import Board as b

# #--------------#
# #  MOVE STEPS  #
# #--------------#

# def in_bounds(tile) :
#    x, y = divmod(tile, 8)
#    return 0 < x < 8 and 0 < y < 8

# def knight_moves(bb): # https://www.chessprogramming.org/Knight_Pattern
#    # https://stackoverflow.com/questions/72296626/chess-bitboard-move-generation#:~:text=When%20you%20generate%20moves%20you,later%20stages%20of%20your%20AI.
#    offsets = [6, 15, 17, 10]

#    moves = []
#    for offset in offsets: 
#       moves.append(bb << offset)
#       moves.append(bb >> offset)

#    for move in moves:
#       b.print_bb(move)
#       print('---------')

   

   


# test = b()
# test.fen_to_board('8/8/8/4N3/3N4/8/8/8 w - - 0 1')
# print(test)
# center = test.pieces['WN']
# b.print_bb(center)
# print('---------')
# knight_moves(test.pieces['WN'])