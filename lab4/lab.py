#!/usr/bin/env python3
"""6.009 Lab -- Six Double-Oh Mines"""

# NO IMPORTS ALLOWED!

def new_board(dimensions, bombs):
    """
    Start a new game.
    Initialize the "board", "mask", "dimensions", and "state" attributes.
    """
    # Initialize board and mask
    mask = make_board(dimensions, False)
    board = make_board(dimensions, 0)
    # Initialize game
    game = {
        "dimensions": dimensions,
        "board": board,
        "mask" : mask,
        "state" : "ongoing",
        }
    # Set bomb in board
    for n in bombs:
        set_coordinate(board, n, '.')
        for neighbor in neighbor_square(dimensions, n):
            value = get_coordinate(game["board"], neighbor)
            if value != '.':
                set_coordinate(game["board"], neighbor, value + 1)
    return game

def make_board(dimensions, element):
    """
    Recursively running make board until len of dimension == 1
    Return an N dimension board
    """
    if len(dimensions) == 1:
        return [element for x in range(dimensions[0])]
    return [make_board(dimensions[1:],element) for x in range(dimensions[0])]

def get_coordinate(board, coordinate):
    """
    Given an N-d array and a tuple/list of coordinates, 
    returns the value at those coordinates in the array.
    """
    if len(coordinate) == 1:
        return board[coordinate[0]]
    return get_coordinate(board[coordinate[0]],coordinate[1:])

def set_coordinate(board, coordinate, value):
    """
    Set the value of a square at the given coordinates on the board.
    """
    if len(coordinate) == 1:
        board[coordinate[0]] = value
    else:
        set_coordinate(board[coordinate[0]],coordinate[1:],value)

def neighbor_square(dimension, coordinate):
    """
    Return a list of neighbors of square
    """
    neighborList = []
    neighbors(dimension, coordinate, 0, neighborList)
    return neighborList
    
def neighbors(dimension, coordinate, index, neighbor):
    """
    Return the neighbors of coordinate
    """
    if index == len(coordinate) - 1:
        for dx in (-1,0,1):
            coord = list(coordinate)
            coord[index] += dx
            if in_bounds(dimension, coord):
                neighbor.append(coord)
    else:
        for dx in (-1,0,1):
            coord = list(coordinate)
            coord[index] += dx
            neighbors(dimension, coord, index+1, neighbor)
    return neighbor
    
def in_bounds(dimension, coords):
    """
    Return whether the coordinates are within bound
    """
    for c,d in zip(coords, dimension):
        if c < 0 or c >= d:
            return False
    return True

def dig(game, coordinate):
    """
    Recursively dig up square at coords and neighboring squares.

    Update the mask to reveal square at coords; then recursively reveal its
    neighbors, as long as coords does not contain and is not adjacent to a
    bomb.  Return a number indicating how many squares were revealed.  No
    action should be taken and 0 returned if the incoming state of the game
    is not 'ongoing'.

    The updated state is 'defeat' when at least one bomb is visible on the
    board after digging, 'victory' when all safe squares (squares that do
    not contain a bomb) and no bombs are visible, and 'ongoing' otherwise.

    Args:
        coords (tuple): Where to start digging

    Returns:
        int: number of squares revealed
    """
    #if defeated or already dug
    if game["state"] != "ongoing" or get_coordinate(game["mask"], coordinate):
        return 0

    #if defeated or already dug
    if get_coordinate(game["board"], coordinate) == '.':
        set_coordinate(game["mask"], coordinate, True)
        game["state"] = "defeat"
        return 1
    else:
        count = reveal_squares(game, coordinate)
        if victory_state(game):
            game["state"] = "victory"
        return count

def reveal_squares(game, coordinate):
    """
    Recursively reveal squares on the board, and return
    the number of squares that were revealed.
    """
    count = 1
    set_coordinate(game["mask"], coordinate, True)
    #if digging up a regular square, recursively dig its neighbors
    if get_coordinate(game["board"],coordinate) == 0:
        for neighbor in neighbor_square(game["dimensions"], coordinate):
            if not get_coordinate(game["mask"], neighbor):
                count += reveal_squares(game, neighbor)
    return count
    
def possibleCoordinates(dimensions):
    """
    Return a list of possible coordinate in a dimension.
    For example:
    dimensions: (2, 3, 4)
    Return: [[0, 0, 0], [0, 0, 1], [0, 0, 2], [0, 0, 3], [0, 1, 0], [0, 1, 1], 
             [0, 1, 2], [0, 1, 3], [0, 2, 0], [0, 2, 1], [0, 2, 2], [0, 2, 3], 
             [1, 0, 0], [1, 0, 1], [1, 0, 2], [1, 0, 3], [1, 1, 0], [1, 1, 1], 
             [1, 1, 2], [1, 1, 3], [1, 2, 0], [1, 2, 1], [1, 2, 2], [1, 2, 3]]
    """
    coordinate = []
    if len(dimensions) == 1:
        for i in range(dimensions[0]):
            coord = [i]
            coordinate.append(coord)
        return coordinate
    
    for i in range(dimensions[0]):
        for coord0 in possibleCoordinates(dimensions[1:]):
            coord = [i]+coord0
            coordinate.append(coord)
    return coordinate

def victory_state(game):
    """
    Check if game is in victory state
    Return True if is in victory state
    """
    covered_squares = 0
    allCoordinates = possibleCoordinates(game["dimensions"])
    for coordinate in allCoordinates:
        board = get_coordinate(game["board"], coordinate)
        mask = get_coordinate(game["mask"], coordinate)
        # if board == '.' and mask:
        #     return False
        if board != '.' and not mask:
            covered_squares += 1
    return True if covered_squares == 0 else False

def dump(game):
    """
    Prints a human-readable version of a game (provided as a dictionary)
    """
    for key, val in sorted(game.items()):
        if isinstance(val, list) and val and isinstance(val[0], list):
            print(f'{key}:')
            for inner in val:
                print(f'    {inner}')
        else:
            print(f'{key}:', val)

# 2-D IMPLEMENTATION
def new_game_2d(num_rows, num_cols, bombs):
    """
    Start a new game.

    Return a game state dictionary, with the 'dimensions', 'state', 'board' and
    'mask' fields adequately initialized.

    Parameters:
       num_rows (int): Number of rows
       num_cols (int): Number of columns
       bombs (list): List of bombs, given in (row, column) pairs, which are
                     tuples

    Returns:
       A game state dictionary

    >>> dump(new_game_2d(2, 4, [(0, 0), (1, 0), (1, 1)]))
    board:
        ['.', 3, 1, 0]
        ['.', '.', 1, 0]
    dimensions: (2, 4)
    mask:
        [False, False, False, False]
        [False, False, False, False]
    state: ongoing
    """
    return new_board((num_rows, num_cols), bombs)
    
def dig_2d(game, row, col):
    """
    Reveal the cell at (row, col), and, in some cases, recursively reveal its
    neighboring squares.

    Update game['mask'] to reveal (row, col).  Then, if (row, col) has no
    adjacent bombs (including diagonally), then recursively reveal (dig up) its
    eight neighbors.  Return an integer indicating how many new squares were
    revealed in total, including neighbors, and neighbors of neighbors, and so
    on.

    The state of the game should be changed to 'defeat' when at least one bomb
    is visible on the board after digging (i.e. game['mask'][bomb_location] ==
    True), 'victory' when all safe squares (squares that do not contain a bomb)
    and no bombs are visible, and 'ongoing' otherwise.

    Parameters:
       game (dict): Game state
       row (int): Where to start digging (row)
       col (int): Where to start digging (col)

    Returns:
       int: the number of new squares revealed

    >>> game = {'dimensions': (2, 4),
    ...         'board': [['.', 3, 1, 0],
    ...                   ['.', '.', 1, 0]],
    ...         'mask': [[False, True, False, False],
    ...                  [False, False, False, False]],
    ...         'state': 'ongoing'}
    >>> dig_2d(game, 0, 3)
    4
    >>> dump(game)
    board:
        ['.', 3, 1, 0]
        ['.', '.', 1, 0]
    dimensions: (2, 4)
    mask:
        [False, True, True, True]
        [False, False, True, True]
    state: victory

    >>> game = {'dimensions': [2, 4],
    ...         'board': [['.', 3, 1, 0],
    ...                   ['.', '.', 1, 0]],
    ...         'mask': [[False, True, False, False],
    ...                  [False, False, False, False]],
    ...         'state': 'ongoing'}
    >>> dig_2d(game, 0, 0)
    1
    >>> dump(game)
    board:
        ['.', 3, 1, 0]
        ['.', '.', 1, 0]
    dimensions: [2, 4]
    mask:
        [True, True, False, False]
        [False, False, False, False]
    state: defeat
    """
    return dig(game, (row, col))

def render_2d(game, xray=False):
    """
    Prepare a game for display.

    Returns a two-dimensional array (list of lists) of '_' (hidden squares), '.'
    (bombs), ' ' (empty squares), or '1', '2', etc. (squares neighboring bombs).
    game['mask'] indicates which squares should be visible.  If xray is True (the
    default is False), game['mask'] is ignored and all cells are shown.

    Parameters:
       game (dict): Game state
       xray (bool): Whether to reveal all tiles or just the ones allowed by
                    game['mask']

    Returns:
       A 2D array (list of lists)

    >>> render_2d({'dimensions': (2, 4),
    ...         'state': 'ongoing',
    ...         'board': [['.', 3, 1, 0],
    ...                   ['.', '.', 1, 0]],
    ...         'mask':  [[False, True, True, False],
    ...                   [False, False, True, False]]}, False)
    [['_', '3', '1', '_'], ['_', '_', '1', '_']]

    >>> render_2d({'dimensions': (2, 4),
    ...         'state': 'ongoing',
    ...         'board': [['.', 3, 1, 0],
    ...                   ['.', '.', 1, 0]],
    ...         'mask':  [[False, True, False, True],
    ...                   [False, False, False, True]]}, True)
    [['.', '3', '1', ' '], ['.', '.', '1', ' ']]
    """
    rows, cols = game["dimensions"]
    return [["_" if (not xray) and (not game["mask"][r][c]) else " " if game["board"][r][c] == 0 
            else str(game["board"][r][c]) for c in range(cols)] for r in range(rows)]

def render_ascii(game, xray=False):
    """
    Render a game as ASCII art.

    Returns a string-based representation of argument 'game'.  Each tile of the
    game board should be rendered as in the function 'render_2d(game)'.

    Parameters:
       game (dict): Game state
       xray (bool): Whether to reveal all tiles or just the ones allowed by
                    game['mask']

    Returns:
       A string-based representation of game

    >>> print(render_ascii({'dimensions': (2, 4),
    ...                     'state': 'ongoing',
    ...                     'board': [['.', 3, 1, 0],
    ...                               ['.', '.', 1, 0]],
    ...                     'mask':  [[True, True, True, False],
    ...                               [False, False, True, False]]}))
    .31_
    __1_
    """
    return "\n".join("".join(r) for r in render_2d(game, xray))

# N-D IMPLEMENTATION
def new_game_nd(dimensions, bombs):
    """
    Start a new game.

    Return a game state dictionary, with the 'dimensions', 'state', 'board' and
    'mask' fields adequately initialized.


    Args:
       dimensions (tuple): Dimensions of the board
       bombs (list): Bomb locations as a list of lists, each an
                     N-dimensional coordinate

    Returns:
       A game state dictionary

    >>> g = new_game_nd((2, 4, 2), [(0, 0, 1), (1, 0, 0), (1, 1, 1)])
    >>> dump(g)
    board:
        [[3, '.'], [3, 3], [1, 1], [0, 0]]
        [['.', 3], [3, '.'], [1, 1], [0, 0]]
    dimensions: (2, 4, 2)
    mask:
        [[False, False], [False, False], [False, False], [False, False]]
        [[False, False], [False, False], [False, False], [False, False]]
    state: ongoing
    """
    return new_board(dimensions, bombs)

def dig_nd(game, coordinates):
    """
    Recursively dig up square at coords and neighboring squares.

    Update the mask to reveal square at coords; then recursively reveal its
    neighbors, as long as coords does not contain and is not adjacent to a
    bomb.  Return a number indicating how many squares were revealed.  No
    action should be taken and 0 returned if the incoming state of the game
    is not 'ongoing'.

    The updated state is 'defeat' when at least one bomb is visible on the
    board after digging, 'victory' when all safe squares (squares that do
    not contain a bomb) and no bombs are visible, and 'ongoing' otherwise.

    Args:
       coords (tuple): Where to start digging

    Returns:
       int: number of squares revealed

    >>> g = {'dimensions': (2, 4, 2),
    ...      'board': [[[3, '.'], [3, 3], [1, 1], [0, 0]],
    ...                [['.', 3], [3, '.'], [1, 1], [0, 0]]],
    ...      'mask': [[[False, False], [False, True], [False, False], [False, False]],
    ...               [[False, False], [False, False], [False, False], [False, False]]],
    ...      'state': 'ongoing'}
    >>> dig_nd(g, (0, 3, 0))
    8
    >>> dump(g)
    board:
        [[3, '.'], [3, 3], [1, 1], [0, 0]]
        [['.', 3], [3, '.'], [1, 1], [0, 0]]
    dimensions: (2, 4, 2)
    mask:
        [[False, False], [False, True], [True, True], [True, True]]
        [[False, False], [False, False], [True, True], [True, True]]
    state: ongoing
    >>> g = {'dimensions': (2, 4, 2),
    ...      'board': [[[3, '.'], [3, 3], [1, 1], [0, 0]],
    ...                [['.', 3], [3, '.'], [1, 1], [0, 0]]],
    ...      'mask': [[[False, False], [False, True], [False, False], [False, False]],
    ...               [[False, False], [False, False], [False, False], [False, False]]],
    ...      'state': 'ongoing'}
    >>> dig_nd(g, (0, 0, 1))
    1
    >>> dump(g)
    board:
        [[3, '.'], [3, 3], [1, 1], [0, 0]]
        [['.', 3], [3, '.'], [1, 1], [0, 0]]
    dimensions: (2, 4, 2)
    mask:
        [[False, True], [False, True], [False, False], [False, False]]
        [[False, False], [False, False], [False, False], [False, False]]
    state: defeat
    """
    return dig(game, coordinates)

def render_nd(game, xray=False):
    """
    Prepare the game for display.

    Returns an N-dimensional array (nested lists) of '_' (hidden squares),
    '.' (bombs), ' ' (empty squares), or '1', '2', etc. (squares
    neighboring bombs).  The mask indicates which squares should be
    visible.  If xray is True (the default is False), the mask is ignored
    and all cells are shown.

    Args:
       xray (bool): Whether to reveal all tiles or just the ones allowed by
                    the mask

    Returns:
       An n-dimensional array of strings (nested lists)

    >>> g = {'dimensions': (2, 4, 2),
    ...      'board': [[[3, '.'], [3, 3], [1, 1], [0, 0]],
    ...                [['.', 3], [3, '.'], [1, 1], [0, 0]]],
    ...      'mask': [[[False, False], [False, True], [True, True], [True, True]],
    ...               [[False, False], [False, False], [True, True], [True, True]]],
    ...      'state': 'ongoing'}
    >>> render_nd(g, False)
    [[['_', '_'], ['_', '3'], ['1', '1'], [' ', ' ']],
     [['_', '_'], ['_', '_'], ['1', '1'], [' ', ' ']]]

    >>> render_nd(g, True)
    [[['3', '.'], ['3', '3'], ['1', '1'], [' ', ' ']],
     [['.', '3'], ['3', '.'], ['1', '1'], [' ', ' ']]]
    """
    dimension = game["dimensions"]
    Gamecopy = make_board(dimension, None)
    for coordinate in possibleCoordinates(dimension):
        if not xray and not get_coordinate(game["mask"], coordinate):
            set_coordinate(Gamecopy, coordinate, "_")
        elif get_coordinate(game["board"], coordinate) == 0:
            set_coordinate(Gamecopy, coordinate, " ")
        else: 
            value = str(get_coordinate(game["board"], coordinate))
            set_coordinate(Gamecopy, coordinate, value)
    return Gamecopy

if __name__ == "__main__":
    # Test with doctests. Helpful to debug individual lab.py functions.
    import doctest
    _doctest_flags = doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS
    doctest.testmod(optionflags=_doctest_flags) #runs ALL doctests

    # Alternatively, can run the doctests JUST for specified function/methods,
    # e.g., for render_2d or any other function you might want.  To do so, comment
    # out the above line, and uncomment the below line of code. This may be
    # useful as you write/debug individual doctests or functions.  Also, the
    # verbose flag can be set to True to see all test results, including those
    # that pass.
    #
    #doctest.run_docstring_examples(render_2d, globals(), optionflags=_doctest_flags, verbose=False)

    # game = new_game_2d(7, 7, [(0, 2), (0, 4), (0, 5), (0, 6), (1, 1), (1, 3), (2, 1), (3, 1),
    #                                 (4, 1), (4, 4), (4, 6), (5, 1), (5, 4), (5, 5), (6, 2), (6, 3),
    #                                 (6, 4)])
    # print(dig_2d(game, 3, 0))
    # print(dig_2d(game, 2, 6))
    # game = {
    #     'dimensions': (4, 3, 2),
    #     'board': [[[1, 1], ['.', 2], [2, 2]], [[1, 1], [2, 2], ['.', 2]],
    #          [[1, 1], [2, 2], [1, 1]], [[1, '.'], [1, 1], [0, 0]]],
    #     'mask': [[[True, False], [False, False], [False, False]], [[False, False], [True, False], [False, False]],
    #         [[False, False], [True, True], [True, True]], [[False, False], [True, True], [True, True]]],
    #     'state': 'ongoing',
    # }
    # # print(get_value(game['board'], (0, 1, 0)))
    # GameCopy = Mines((1,1,1), [])
    # GameCopy.copy_from_dict(game)
    # print(GameCopy.neighbor_sqaure((0, 1, 0)))
    # print(GameCopy.return_in_form())
    # print(neighbor_square((10,), (5,)))
    # print(neighbor_square((10, 20), (5, 13)))
    # print(neighbor_square((10, 20, 3), (5, 13, 0)))