import logging

logging.basicConfig(level=logging.DEBUG)

LOGGER = logging.getLogger('pysudoku')


def read_puzzles_from_file(puzfile):
    """
    Read puzzle files as from http://magictour.free.fr/sudoku.htm
    """
    fptr = open(puzfile, 'r')
    lines = fptr.readlines()
    fptr.close()
    puzzles = []
    for line in lines:
        if len(line) < 40:
            break
        puz = []
        for idx in range(0, 81):
            val = line[idx]
            if val == '.':
                puz.append(-1)
            else:
                puz.append(int(val))
        puzzles.append(puz)
    return puzzles

filename = '/home/paulp/projects/sudoku.github/puzzles/subig20.txt'
filename = '/home/paulp/projects/sudoku.github/puzzles/top870.txt'

#filename = '/home/paulp/projects/code/sudoku.github/puzzles/top870.txt'

puzzles = read_puzzles_from_file(filename)
print 'Loaded %i puzzles from %s.' % (len(puzzles), filename)

class Puzzle(object):
    """
    A Sudoku puzzle.
    """
    def __init__(self, puzzle):
        self.puzzle = puzzle
        self.blocks = []

        # make the blocks
        self.unknown_blocks = []
        for row in xrange(0, 9):
            for col in xrange(0, 9):
                blk = Block(self.blocks, row, col)
                self.blocks.append(blk)
                self.unknown_blocks.append(blk.idx)
                # print blk.idx
                # blk.print_mates()

        self.print_puzzle(True)

        # update the blocks from the initial values
        for idx in range(0, 81):
            if self.puzzle[idx] > 0:
                self.blocks[idx].set_value(self.puzzle[idx])

    def print_puzzle(self, original=False):
        for row in range(9):
            for col in range(9):
                idx = Puzzle.idx_from_addr((row, col))
                if original:
                    puz_val = self.puzzle[idx]
                    if puz_val == -1:
                        print '  .',
                    else:
                        print '%3i' % puz_val,
                else:
                    blk = self.blocks[idx]
                    if blk.val == -1:
                        print '  .',
                    else:
                        print '%3i' % blk.val,
            print ''
        print ''

    def unsolved(self):
        """
        How many unsolved blocks are there?
        :return:
        """
        return len(self.unknown_blocks)

    def run_type_1(self):
        """
        If a possible only occurs once in a row, col or cel,
        then it must be that value
        :return:
        """
        for rcc in [ROWS, COLS, CELS]:
            for rowctr, row in enumerate(rcc):
                rpos = {}
                for idx in row:
                    for pos in self.blocks[idx].pos:
                        if pos not in rpos:
                            rpos[pos] = []
                        rpos[pos].append(idx)
                LOGGER.debug('RCC %i possibles: %s' % (rowctr, rpos))
                for pos in rpos:
                    if len(rpos[pos]) == 1:
                        LOGGER.debug('          block %i can only be %i' % (rpos[pos][0], pos))
                        blk = self.blocks[rpos[pos][0]]
                        blk.set_value(pos)

    # method to use the line eliminator method
    def run_line_eliminator(self):
        for cel in CELS:
            raise NotImplementedError

    def run_pairs(self):
        for rcc in [ROWS, COLS, CELS]:
            for rowctr, row in enumerate(rcc):
                pairs = []
                for idx in row:
                    blk = self.blocks[idx]
                    if len(blk.pos) == 2:
                        pairs.append(idx)
                if len(pairs) == 2:
                    if self.blocks[pairs[0]].pos == self.blocks[pairs[1]].pos:
                        raise RuntimeError('yay')
                        print pairs[0], self.blocks[pairs[0]].pos
                        print pairs[1], self.blocks[pairs[1]].pos

    def run_triples(self):
        for rcc in [ROWS, COLS, CELS]:
            for rowctr, row in enumerate(rcc):
                pairs = []
                for idx in row:
                    blk = self.blocks[idx]
                    if len(blk.pos) == 3:
                        pairs.append(idx)
                if len(pairs) == 3:
                    if (self.blocks[pairs[0]].pos == self.blocks[pairs[1]].pos) and\
                            (self.blocks[pairs[0]].pos == self.blocks[pairs[2]].pos):
                        raise RuntimeError('yay')
                        print pairs[0], self.blocks[pairs[0]].pos
                        print pairs[1], self.blocks[pairs[1]].pos


    def get_pos(self):
        # get the possibles again
        nz_pos = 0
        for row in xrange(0, 9):
            rowstring = ''
            for col in xrange(0, 9):
                blk = self.blocks[Puzzle.idx_from_addr((row, col))]
                rowstring += '%3i ' % len(blk.pos)
                if blk.pos:
                    nz_pos += 1
            LOGGER.debug(rowstring)
        return nz_pos

    @staticmethod
    def idx_from_addr(addr):
        return (addr[0] * 9) + addr[1]

    @staticmethod
    def addr_from_idx(idx):
        row = idx / 9
        col = idx - (row * 9)
        return row, col

    @staticmethod
    def cel_from_idx(idx):
        addr = Puzzle.addr_from_idx(idx)
        return Puzzle.cel_from_addr(addr)

    @staticmethod
    def cel_from_addr(addr):
        cel_col = addr[1] / 3
        cel_row = addr[0] / 3
        return (cel_row * 3) + cel_col

    @staticmethod
    def celmates(cel=None, idx=None, addr=None):
        if cel is not None:
            return Puzzle._celmates_from_cel(cel)
        elif idx is not None:
            return Puzzle._celmates_from_idx(idx)
        elif addr is not None:
            return Puzzle._celmates_from_addr(addr)
        raise ValueError('Unspecified action')

    @staticmethod
    def _celmates_from_idx(idx):
        cel = Puzzle.cel_from_idx(idx)
        return Puzzle._celmates_from_cel(cel)

    @staticmethod
    def _celmates_from_addr(addr):
        cel = Puzzle.cel_from_addr(addr)
        return Puzzle._celmates_from_cel(cel)

    @staticmethod
    def _celmates_from_cel(cel_num):
        col_start = (cel_num % 3) * 3
        row_start = (cel_num / 3) * 3
        celmates = []
        for row in range(row_start, row_start + 3):
            for col in range(col_start, col_start + 3):
                celmates.append(Puzzle.idx_from_addr((row, col)))
        return celmates

    @staticmethod
    def rowmates(row):
        rowstart = row * 9
        return range(rowstart, rowstart + 9)

    @staticmethod
    def colmates(col):
        return range(col, 9*9, 9)

ROWS = [range(idx, idx+9) for idx in range(0, 81, 9)]
COLS = [range(idx, 81, 9) for idx in range(9)]
CELS = [Puzzle._celmates_from_cel(idx) for idx in range(9)]


print CELS

raise RuntimeError

class Block(object):
    def __init__(self, block_list, row, col, val=-1):
        self.idx = Puzzle.idx_from_addr((row, col))
        self.row = row
        self.col = col
        self.cel = Puzzle.cel_from_addr((row, col))
        self.celmates = Puzzle.celmates(cel=self.cel)
        self.celmates.pop(self.celmates.index(self.idx))
        self.rowmates = Puzzle.rowmates(row=self.row)
        self.rowmates.pop(self.rowmates.index(self.idx))
        self.colmates = Puzzle.colmates(col=self.col)
        self.colmates.pop(self.colmates.index(self.idx))
        self.areamates = self.celmates[:]
        self.areamates.extend(self.rowmates)
        self.areamates.extend(self.colmates)
        self.areamates = list(set(self.areamates))
        self.val = val
        self.pos = range(1, 10)
        if val > 0:
            self.pos = []
        self.blks = block_list

    def print_mates(self):
        for row in range(9):
            for col in range(9):
                idx = Puzzle.idx_from_addr((row, col))
                if idx == self.idx:
                    print ' @',
                elif idx in self.areamates:
                    print ' *',
                else:
                    print ' .',

            print 10*' ',
            for col in range(9):
                idx = Puzzle.idx_from_addr((row, col))
                if idx == self.idx:
                    print ' @',
                elif idx in self.celmates:
                    print ' *',
                else:
                    print ' .',

            print 10*' ',
            for col in range(9):
                idx = Puzzle.idx_from_addr((row, col))
                if idx == self.idx:
                    print ' @',
                elif idx in self.rowmates:
                    print ' *',
                else:
                    print ' .',

            print 10*' ',
            for col in range(9):
                idx = Puzzle.idx_from_addr((row, col))
                if idx == self.idx:
                    print ' @',
                elif idx in self.colmates:
                    print ' *',
                else:
                    print ' .',

            print ''

    def print_area_mates(self):
        for row in range(9):
            for col in range(9):
                idx = Puzzle.idx_from_addr((row, col))
                if idx == self.idx:
                    print ' @',
                elif idx in self.areamates:
                    print ' *',
                else:
                    print ' .',
            print ''

    def print_row_mates(self):
        for row in range(9):
            for col in range(9):
                idx = Puzzle.idx_from_addr((row, col))
                if idx == self.idx:
                    print ' @',
                elif idx in self.rowmates:
                    print ' *',
                else:
                    print ' .',
            print ''

    def print_col_mates(self):
        for row in range(9):
            for col in range(9):
                idx = Puzzle.idx_from_addr((row, col))
                if idx == self.idx:
                    print ' @',
                elif idx in self.colmates:
                    print ' *',
                else:
                    print ' .',
            print ''

    def set_value(self, val):
        LOGGER.debug('%i: updating val -> %i - %s' % (self.idx, val, 50 * '*'))
        self.val = val
        self.pos = []
        for idx in self.areamates:
            self.blks[idx].update_pos(val)

    def update_pos(self, val):
        if len(self.pos) == 0:
            return
        LOGGER.debug('%i: removing possible %i' % (self.idx, val))
        try:
            idx = self.pos.index(val)
            self.pos.pop(idx)
            removed = True
            LOGGER.debug('       pos(%i) found at index %i, removed' % (val, idx))
        except ValueError:
            removed = False
            LOGGER.debug('       pos(%i) not found.' % val)
        if len(self.pos) == 1:
            if not removed:
                raise RuntimeError('How did this happen? Why was it not'
                                   'updated before this?')
            if self.val != -1:
                raise RuntimeError('Cannot have len(pos)==1 and val!=-1')
            LOGGER.debug('       %i: now only one possible left, updating -> %i' %
                         (self.idx, self.pos[0]))
            self.set_value(self.pos[0])

puz_solved = 0
puz_failed = 0
# for puzctr in range(len(puzzles)):
# for puzctr in range(314,315):
for puzctr in range(1,2):

    print 'puzzle', puzctr

    puz = Puzzle(puzzles[puzctr])

    puz.print_puzzle()

    # run searches
    puz.run_type_1()
    puz.run_pairs()

    nonzero_pos = puz.get_pos()
    if nonzero_pos > 0:
        # print 'puzzle %06i: NOT SOLVED' % puzctr
        puz_failed += 1
    else:
        # print 'puzzle %06i: okay' % puzctr
        puz_solved += 1

    puz.print_puzzle()

print 'solved(%i) failed(%i)' % (puz_solved, puz_failed)

    # # print possibles
    # #
    # # for row in xrange(0, 9):
    # #     print blocks[row]
    #
    # # for row in xrange(0, 9):
    # #     for col in xrange(0, 9):
    # #         print '%d, ' % cell_from_index(row, col),
    # #     print ''
    # #
    # # for cell in xrange(0, 9):
    # #     print cell_mates(cell)
    # #
    # #
    # # print possibles
    #
    # for row in xrange(0, 9):
    #     for col in xrange(0, 9):
    #         this_value = blocks[row][col]
    #         these_possibles = possibles[row][col]
    #         this_cell = cell_from_index(row, col)
    #         if this_value != -1:
    #             possibles[row][col] = []
    #             continue
    #         # search my column
    #         for searchrow in xrange(0, 9):
    #             try:
    #                 index = these_possibles.index(blocks[searchrow][col])
    #                 these_possibles.pop(index)
    #             except ValueError:
    #                 pass
    #         # search my row
    #         for searchcol in xrange(0, 9):
    #             try:
    #                 index = these_possibles.index(blocks[row][searchcol])
    #                 these_possibles.pop(index)
    #             except ValueError:
    #                 pass
    #         # search my cell
    #         for celmates in cell_mates(this_cell):
    #             try:
    #                 index = these_possibles.index(blocks[celmates[0]][celmates[1]])
    #                 these_possibles.pop(index)
    #             except ValueError:
    #                 pass
    #         # are we down to one value?
    #         if len(these_possibles) == 1:
    #             print row, col, this_value, these_possibles
    #
    # print possibles
    #
    # raise RuntimeError
    #
    # for row in xrange(0, 9):
    #     for col in xrange(0, 9):
    #         print row, col, cell_from_index(row, col), possibles[row][col]


    # initial values
    # blocks[idx_from_addr((0, 1))].set_value(5)
    # blocks[idx_from_addr((0, 3))].set_value(4)
    # blocks[idx_from_addr((0, 6))].set_value(8)
    #
    # blocks[idx_from_addr((1, 2))].set_value(7)
    # blocks[idx_from_addr((1, 8))].set_value(9)
    #
    # blocks[idx_from_addr((2, 0))].set_value(4)
    # blocks[idx_from_addr((2, 4))].set_value(1)
    # blocks[idx_from_addr((2, 7))].set_value(6)
    #
    # blocks[idx_from_addr((3, 3))].set_value(7)
    # blocks[idx_from_addr((3, 5))].set_value(9)
    # blocks[idx_from_addr((3, 8))].set_value(8)
    #
    # blocks[idx_from_addr((4, 2))].set_value(6)
    # blocks[idx_from_addr((4, 4))].set_value(4)
    # blocks[idx_from_addr((4, 6))].set_value(7)
    #
    # blocks[idx_from_addr((5, 0))].set_value(5)
    # blocks[idx_from_addr((5, 3))].set_value(1)
    # blocks[idx_from_addr((5, 5))].set_value(2)
    #
    # blocks[idx_from_addr((6, 1))].set_value(6)
    # blocks[idx_from_addr((6, 4))].set_value(2)
    # blocks[idx_from_addr((6, 8))].set_value(4)
    #
    # blocks[idx_from_addr((7, 0))].set_value(3)
    # blocks[idx_from_addr((7, 6))].set_value(2)
    #
    # blocks[idx_from_addr((8, 2))].set_value(8)
    # blocks[idx_from_addr((8, 5))].set_value(3)
    # blocks[idx_from_addr((8, 7))].set_value(5)
