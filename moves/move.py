
#-------------#
#    FLAGS    #
#-------------#

QUIET = 0
DOUBLE_PUSH = 1
OO = 2
OOO = 3
CAPTURE = 4
EP = 5

PROMOTE_B = 6
PROMOTE_N = 7
PROMOTE_R = 8
PROMOTE_Q = 9

PROMOTE_B_CAP = 10
PROMOTE_N_CAP = 11
PROMOTE_R_CAP = 12
PROMOTE_Q_CAP = 13

#----------------#
#     METHODS    #
#----------------#

def encode_move(start: int, end: int, flag: int):
    '''
    Docstring for encode_move
    
    :param start: Tile shifts from 0
    :type start: int
    :param end: Tile shifts from 0
    :type end: int
    :param flag: Type of move
    :type flag: int
    '''
    moves = flag << 12 | end << 6 | start

    return moves

def get_start(move): 
    return move & 0x3F

def get_end(move):  
    return (move >> 6) & 0x3F
 
def get_flag(move):  
    return (move >> 12) & 0xF