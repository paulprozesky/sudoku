__author__ = 'paulp'

blocks = []

def read_puzzles_from_file(filename):
    """
    Read puzzle files as from http://magictour.free.fr/sudoku.htm
    """
    fptr = open(filename, 'r')
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

puzzles = read_puzzles_from_file('/home/paulp/projects/sudoku.github/puzzles/subig20.txt')
print 'Loaded %i puzzles.' % len(puzzles)

def idx_from_addr(addr):
    return (addr[0] * 9) + addr[1]


def addr_from_idx(idx):
    row = idx / 9
    col = idx - (row * 9)
    return row, col


def cel_from_idx(idx):
    addr = addr_from_idx(idx)
    return cel_from_addr(addr)


def cel_from_addr(addr):
    cel_col = addr[1] / 3
    cel_row = addr[0] / 3
    return (cel_row * 3) + cel_col


def celmates(cel=None, idx=None, addr=None):
    if cel is not None:
        return _celmates_from_cel(cel)
    elif idx is not None:
        return _celmates_from_idx(idx)
    elif addr is not None:
        return _celmates_from_addr(addr)
    raise ValueError('Unspecified action')


def _celmates_from_idx(idx):
    cel = cel_from_idx(idx)
    return _celmates_from_cel(cel)


def _celmates_from_addr(addr):
    cel = cel_from_addr(addr)
    return _celmates_from_cel(cel)


def _celmates_from_cel(cel_num):
    col_start = (cel_num % 3) * 3
    row_start = (cel_num / 3) * 3
    celmates = []
    for row in xrange(row_start, row_start + 3):
        for col in xrange(col_start, col_start + 3):
            celmates.append(idx_from_addr((row, col)))
    return celmates


def rowmates(row):
    rowstart = row * 9
    return range(rowstart, rowstart + 9)


def colmates(col):
    return range(col, 9*9, 9)


class Block(object):
    def __init__(self, row, col, val=-1):
        self.idx = idx_from_addr((row, col))
        self.row = row
        self.col = col
        self.cel = cel_from_addr((row, col))
        self.celmates = celmates(cel=self.cel)
        self.celmates.pop(self.celmates.index(self.idx))
        self.rowmates = rowmates(row=self.row)
        self.rowmates.pop(self.rowmates.index(self.idx))
        self.colmates = colmates(col=self.col)
        self.colmates.pop(self.colmates.index(self.idx))
        self.areamates = self.celmates[:]
        self.areamates.extend(self.rowmates)
        self.areamates.extend(self.colmates)
        self.areamates = list(set(self.areamates))
        self.val = val
        self.pos = range(1, 10)
        if val > 0:
            self.pos = []

    def set_value(self, val):
        self.val = val
        self.pos = []
        for idx in self.celmates:
            blocks[idx].update_pos(val)
        for idx in self.rowmates:
            blocks[idx].update_pos(val)
        for idx in self.colmates:
            blocks[idx].update_pos(val)

    def update_pos(self, val):
        if len(self.pos) == 0:
            return
        try:
            idx = self.pos.index(val)
            self.pos.pop(idx)
        except ValueError:
            pass
        if len(self.pos) == 1:
            if self.val != -1:
                raise RuntimeError('Cannot have len(pos)==1 and val!=-1')
            print 'update_pos: block(%i,%i) value -> %i' % \
                  (self.row, self.col, self.pos[0])
            self.set_value(self.pos[0])

    def search_pos_1(self):
        """
        Type 1 search - does a possible only exist in one place in
        a row, col or cel?
        """
        def searchmates(mates_idx):
            rowpos = {}
            for idx in mates_idx:
                for pos in blocks[idx].pos:
                    if pos not in rowpos:
                        rowpos[pos] = []
                    rowpos[pos].append(idx)
            for posval in rowpos:
                if len(rowpos[posval]) == 1:
                    blk = blocks[rowpos[posval][0]]
                    print 'search_pos_1: block(%i,%i) value -> %i' % \
                          (blk.row, blk.col, posval)
                    blk.set_value(posval)
        searchmates(self.rowmates)
        searchmates(self.colmates)
        searchmates(self.celmates)

    def solve_pairs(self):
        """
        Look for pairs of possibles
        :return:
        """
        twopos = []
        for idx in self.areamates:
            if len(blocks[idx].pos) == 2:
                twopos.append(idx)
        if len(twopos) == 2:
            raise RuntimeError('yay')
        elif len(twopos) > 2:
            raise RuntimeError('this is not possible')

for puzctr in range(0, 10):

    puz = puzzles[puzctr]

    # make the blocks
    blocks = []
    for row in xrange(0, 9):
        for col in xrange(0, 9):
            blk = Block(row, col)
            blocks.append(blk)
            print '%3i ' % blk.cel,
        print ''

    print puz
    for idx in range(0, 81):
        if puz[idx] > 0:
            blocks[idx].set_value(puz[idx])

    blk = blocks[0]
    print blk.celmates
    print blk.rowmates
    print blk.colmates
    print blk.areamates
    # raise RuntimeError

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

    for loopctr in range(0, 1):

        # show the possibles
        for row in xrange(0, 9):
            for col in xrange(0, 9):
                blk = blocks[idx_from_addr((row, col))]
                print '%3i ' % len(blk.pos),
            print ''

        # run a type 1 search
        for row in xrange(0, 9):
            for col in xrange(0, 9):
                blk = blocks[idx_from_addr((row, col))]
                blk.search_pos_1()

        for row in xrange(0, 9):
            for col in xrange(0, 9):
                blk = blocks[idx_from_addr((row, col))]
                blk.solve_pairs()

        print ''

        # show the possibles again
        for row in xrange(0, 9):
            for col in xrange(0, 9):
                blk = blocks[idx_from_addr((row, col))]
                print '%3i ' % len(blk.pos),
            print ''

        # show the values
        for row in xrange(0, 9):
            for col in xrange(0, 9):
                blk = blocks[idx_from_addr((row, col))]
                print '%2i ' % blk.val,
            print ''

        print 80 * '*'

    continue

    # print possibles
    #
    # for row in xrange(0, 9):
    #     print blocks[row]

    # for row in xrange(0, 9):
    #     for col in xrange(0, 9):
    #         print '%d, ' % cell_from_index(row, col),
    #     print ''
    #
    # for cell in xrange(0, 9):
    #     print cell_mates(cell)
    #
    #
    # print possibles

    for row in xrange(0, 9):
        for col in xrange(0, 9):
            this_value = blocks[row][col]
            these_possibles = possibles[row][col]
            this_cell = cell_from_index(row, col)
            if this_value != -1:
                possibles[row][col] = []
                continue
            # search my column
            for searchrow in xrange(0, 9):
                try:
                    index = these_possibles.index(blocks[searchrow][col])
                    these_possibles.pop(index)
                except ValueError:
                    pass
            # search my row
            for searchcol in xrange(0, 9):
                try:
                    index = these_possibles.index(blocks[row][searchcol])
                    these_possibles.pop(index)
                except ValueError:
                    pass
            # search my cell
            for celmates in cell_mates(this_cell):
                try:
                    index = these_possibles.index(blocks[celmates[0]][celmates[1]])
                    these_possibles.pop(index)
                except ValueError:
                    pass
            # are we down to one value?
            if len(these_possibles) == 1:
                print row, col, this_value, these_possibles

    print possibles

    raise RuntimeError

    for row in xrange(0, 9):
        for col in xrange(0, 9):
            print row, col, cell_from_index(row, col), possibles[row][col]