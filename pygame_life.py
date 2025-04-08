"""
    Pygame of life module. Contains the short engine
    to simluate the grid of life.
"""

import sys
import time
from collections import defaultdict
from copy import deepcopy

import pygame

# from example_grids import GOSPER_GLIDER
from grid_defs import Grid, Neighbours, Dim
from random import randint
from itertools import product


def find_offsets_dims(dims):
    base_offsets = []
    for d in range(dims):
        base_offsets.append((-1,0,1))
    offset_list = [p for p in product(*base_offsets)]
    # Remove the central cell
    offset_list.remove(tuple([0 for r in range(dims)]))
    return offset_list


def get_neighbours1(grid: Grid, x: int, y: int) -> Neighbours:
    """
        Gets the neighbour states for a particular cell in
        (x, y) on the grid.
    """
    offsets = [(-1, -1), (0, -1), (1, -1), (-1, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    possible_neighbours = {(x + x_add, y + y_add) for x_add, y_add in offsets}
    alive = {(pos[0], pos[1]) for pos in possible_neighbours if pos in grid.cells}
    return Neighbours(alive, possible_neighbours - alive)


def get_neighbours_2d(grid: Grid, *args) -> Neighbours:
    """
        Gets the neighbour states for a particular cell in
        (x, y) on the grid.
    """
    # offsets = find_offsets_dims(len(args))
    possible_neighbours = moore_range_dimless(*args)
    alive = {(pos[0], pos[1]) for pos in possible_neighbours if pos in grid.cells}
    return Neighbours(alive, possible_neighbours - alive)


def get_neighbours(grid: Grid, *args) -> Neighbours:
    """
        Gets the neighbour states for a particular cell in
        (x, y, z) on the grid.
    """
    possible_neighbours = moore_range_dimless(*args)
    # Restrict neighbours to only the given layers.
    possible_neighbours = {(pos[0], pos[1], pos[2]) for pos in possible_neighbours if pos[0] in range(grid.dim.width)}
    possible_neighbours = {(pos[0], pos[1], pos[2]) for pos in possible_neighbours if pos[1] in range(grid.dim.height)}
    possible_neighbours = {(pos[0], pos[1], pos[2]) for pos in possible_neighbours if pos[2] in range(grid.dim.length)}
    alive = {(pos[0], pos[1], pos[2]) for pos in possible_neighbours if pos in grid.cells}
    return Neighbours(alive, possible_neighbours - alive)


def moore_range_dimless(*args):
    adjacent_coords = []
    for a in args:
        adjacent_coords.append([a-1,a,a+1])
    nb_coords = {p for p in product(*adjacent_coords)}
    # Remove the central cell
    nb_coords.remove(args)
    return nb_coords


def update_grid(grid: Grid, rulestring: str) -> Grid:
    """
        Given a grid, this function returns the next iteration
        of the game of life.
    """
    rs_list = rulestring[1:].split('S')
    b_list = rs_list[0]
    s_list = rs_list[1]
    birth_rule = [int(x) for x in b_list.split(',')]
    survival_rule = [int(x) for x in s_list.split(',')]
    
    new_cells = deepcopy(grid.cells)
    undead = defaultdict(int)

    for x, y, z in grid.cells:
        alive_neighbours, dead_neighbours = get_neighbours(grid, x, y, z)
        # if len(alive_neighbours) not in [2, 3]:
        if len(alive_neighbours) not in survival_rule:
            new_cells.remove((x, y, z))

        for pos in dead_neighbours:
            undead[pos] += 1
        
        print(alive_neighbours)
    
    # for pos, _ in filter(lambda elem: elem[1] == 3, undead.items()):
    for pos, _ in filter(lambda elem: elem[1] in birth_rule, undead.items()):
        new_cells.add((pos[0], pos[1], pos[2]))

    return Grid(grid.dim, new_cells)


def draw_grid(screen: pygame.Surface, grid: Grid) -> None:
    """
        This function draws the game of life on the given
        pygame.Surface object.
    """   
    # Each scene holds one layer.
    layer_width = screen.get_width() / grid.dim.length
    buffer = layer_width - screen.get_height()
    cell_width = screen.get_height() / grid.dim.width 
    cell_height = screen.get_height() / grid.dim.height
    # Separate each scene with a border of a given colour.
    for lg in range(grid.dim.length):
        pygame.draw.rect(
            screen,
            (0, 64, 0),
            (
                (lg+1) * layer_width - buffer,
                0,
                buffer,
                screen.get_height(),
            ),
        )
    

    border_size = 2

    for x, y, z in grid.cells:
        pygame.draw.rect(
            screen,
            (0, 128, 192),
            (
                x * cell_width + z * layer_width + border_size,
                y * cell_height + border_size,
                cell_width - border_size,
                cell_height - border_size,
            ),
        )


def random_grid(threshold: float, len_side: int, length=1) -> Grid:
    layer_area = len_side**2
    size = layer_area * length
    # Generate random number of tuples.
    floor = int(threshold*size)
    # Each tuple contains three random integers within range.
    lc = {randint(0,size-1) for i in range(floor)}
    living_cells = {(l//len_side, l%len_side, l//layer_area) for l in lc}
    return Grid(Dim(len_side, len_side, length), living_cells)
    
    
def main():
    # rulestring = 'B3S2,3'
    rulestring = 'B6S5,6,7'
    # grid = GOSPER_GLIDER
    length = 2
    grid = random_grid(0.5, 20, length)

    pygame.init()
    screen = pygame.display.set_mode((240*length, 200))

    while True:
        if pygame.QUIT in [e.type for e in pygame.event.get()]:
            sys.exit(0)

        screen.fill((0, 0, 0))
        draw_grid(screen, grid)
        grid = update_grid(grid, rulestring)
        pygame.display.flip()
        time.sleep(1.1)


if __name__ == "__main__":
    main()
