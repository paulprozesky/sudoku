__author__ = 'paulp'

import logging

logging.basicConfig(level=logging.INFO)

LOGGER = logging.getLogger('pysudoku')

blocks = []


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

filename = '/home/paulp/projects/code/sudoku.github/puzzles/top870.txt'

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
        for row in xrange(0, 9):
            for col in xrange(0, 9):
                blk = self.blocks[Puzzle.idx_from_addr((row, col))]
                blk.search_pos_1()

    def run_pairs(self):
        for row in xrange(0, 9):
            for col in xrange(0, 9):
                blk = self.blocks[Puzzle.idx_from_addr((row, col))]
                blk.solve_pairs()

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
        for row in xrange(row_start, row_start + 3):
            for col in xrange(col_start, col_start + 3):
                celmates.append(Puzzle.idx_from_addr((row, col)))
        return celmates

    @staticmethod
    def rowmates(row):
        rowstart = row * 9
        return range(rowstart, rowstart + 9)

    @staticmethod
    def colmates(col):
        return range(col, 9*9, 9)


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
        self.val = val
        self.pos = []

        for idx in self.areamates:
            self.blks[idx].update_pos(val)

        # WHYWYWYWY does the above work, but the below not?

        # for idx in self.celmates:
        #     self.blks[idx].update_pos(val)
        # for idx in self.rowmates:
        #     self.blks[idx].update_pos(val)
        # for idx in self.colmates:
        #     self.blks[idx].update_pos(val)

    def update_pos(self, val):
        if len(self.pos) == 0:
            return
        try:
            idx = self.pos.index(val)
            self.pos.pop(idx)
            removed = True
        except ValueError:
            removed = False
        if len(self.pos) == 1:
            if not removed:
                raise RuntimeError('How did this happen? Why was it not'
                                   'updated before this?')
            if self.val != -1:
                raise RuntimeError('Cannot have len(pos)==1 and val!=-1')
            LOGGER.debug('update_pos: block(%i,%i) value -> %i' %
                         (self.row, self.col, self.pos[0]))
            self.set_value(self.pos[0])

    def search_pos_1(self):
        """
        Type 1 search - does a possible only exist in one place in
        a row, col or cel?
        """
        def searchmates(mates_idx):
            rowpos = {}
            for idx in mates_idx:
                for pos in self.blks[idx].pos:
                    if pos not in rowpos:
                        rowpos[pos] = []
                    rowpos[pos].append(idx)
            for posval in rowpos:
                if len(rowpos[posval]) == 1:
                    blk = self.blks[rowpos[posval][0]]
                    LOGGER.debug('search_pos_1: block(%i,%i) value -> %i' %
                                 (blk.row, blk.col, posval))
                    blk.set_value(posval)
        searchmates(self.rowmates)
        searchmates(self.colmates)
        searchmates(self.celmates)

    def solve_pairs(self):
        """
        Look for pairs of possibles - there can be more than two
        blocks that have two possibles, but not more than two
        that have the *same* two possibles!
        :return:
        """
        twopos = []
        search_area = self.areamates[:]
        search_area.append(self.idx)
        for idx in search_area:
            if len(self.blks[idx].pos) == 2:
                twopos.append(idx)

        if len(twopos) > 0:

            for idx in range(81):
                print idx, self.blks[idx].pos, id(self.blks[idx])

            print twopos

            for row in range(9):
                for col in range(9):
                    print '%3i' % self.blks[Puzzle.idx_from_addr((row, col))].val,
                print ''

            raise RuntimeError

        if len(twopos) == 2:
            blk_one = self.blks[twopos[0]]
            blk_two = self.blks[twopos[1]]

            print blk_one.idx, blk_two.idx, blk_one.pos

            for idx in range(81):
                    print idx, self.blks[idx].pos
            raise RuntimeError

            if blk_one.pos == blk_one.pos:
                search_area_minus = search_area[:]

                print search_area_minus

                search_area_minus.pop(search_area_minus.index(blk_one.idx))
                search_area_minus.pop(search_area_minus.index(blk_two.idx))

                print search_area_minus

                for idx in search_area_minus:
                    print idx, self.blks[idx].pos

                    self.blks[idx].update_pos(blk_one.pos[0])
                    self.blks[idx].update_pos(blk_one.pos[1])

                    print idx, self.blks[idx].pos

                raise RuntimeError
            else:
                print blk_one.idx, blk_one.pos
                print blk_two.idx, blk_two.pos
                raise RuntimeError('that is odd - should be the same')

        elif len(twopos) > 2:

            print twopos

            raise RuntimeError('multiples of two are technically '
                               'possible... handle this')

    def solve_triples(self):
        """
        Look for pairs of possibles
        :return:
        """
        threepos = []
        for idx in self.areamates:
            if len(blocks[idx].pos) == 3:
                threepos.append(idx)
        if len(threepos) == 3:
            raise RuntimeError('yay')
        elif len(threepos) > 3:
            raise RuntimeError('this is not possible')


puz_solved = 0
puz_failed = 0
# for puzctr in range(len(puzzles)):
for puzctr in range(314,315):

    print 'puzzle', puzctr

    puz = Puzzle(puzzles[puzctr])

    puz.print_puzzle()

    for loopctr in range(0, 1):

        # run searches
        # puz.run_type_1()
        # puz.run_pairs()

        nonzero_pos = puz.get_pos()
        if nonzero_pos > 0:
            # print 'puzzle %06i: NOT SOLVED' % puzctr
            puz_failed += 1
        else:
            # print 'puzzle %06i: okay' % puzctr
            puz_solved += 1

        # # show the values
        # for row in xrange(0, 9):
        #     for col in xrange(0, 9):
        #         blk = blocks[idx_from_addr((row, col))]
        #         print '%2i ' % blk.val,
        #     print ''

        # print 80 * '*'

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
