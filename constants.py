import random

SIZE = 400
GRID_LEN = 4
GRID_PADDING = 10

BACKGROUND_COLOR_GAME = "#92877d"
BACKGROUND_COLOR_CELL_EMPTY = "#9e948a"

BACKGROUND_COLOR_DICT = {2: "#eee4da", 4: "#ede0c8", 8: "#f2b179",
                         16: "#f59563", 32: "#f67c5f", 64: "#f65e3b",
                         128: "#edcf72", 256: "#edcc61", 512: "#edc850",
                         1024: "#edc53f", 2048: "#edc22e",

                         4096: "#3c3a32", 8192: "#3c3a32", 16384: "#3c3a32",
                         32768: "#3c3a32", 65536: "#3c3a32", }
# default black: #3c3a32
CELL_COLOR_DICT = {2: "#776e65", 4: "#776e65", 8: "#f9f6f2", 16: "#f9f6f2",
                   32: "#f9f6f2", 64: "#f9f6f2", 128: "#f9f6f2",
                   256: "#f9f6f2", 512: "#f9f6f2", 1024: "#f9f6f2",
                   2048: "#f9f6f2",

                   4096: "#f9f6f2", 8192: "#f9f6f2", 16384: "#f9f6f2",
                   32768: "#f9f6f2", 65536: "#f9f6f2", }

ALT_1 = {          4096: "#051005", 8192: "#102010", 16384: "#204020",
                   32768: "#408040", 65536: "#00FF00", }
ALT_2 = {          4096: "#001000", 8192: "#30212b", 16384: "#15aaac",
                   32768: "#15aaac", 65536: "#25f4bc", }
ALT_3 = {          4096: "#637B84", 8192: "#7E969F", 16384: "#84B5CA",
                   32768: "#91CDD5", 65536: "#91D0F8", }               
ALT_4 = {          4096: "#99D9EA", 8192: "#72CCE2", 16384: "#72CCE2",
                   32768: "#27A0BE", 65536: "#1C7388", }
ALT_5 = {          4096: "#6BCE11", 8192: "#67C006", 16384: "#5DB803",
                   32768: "#51A905", 65536: "#4C8914", }


def switch_cell_palette():
    ALTS = [ALT_1,ALT_2,ALT_3,ALT_4,ALT_5]
    ind = random.randint(0,len(ALTS)-1)
    palette = ALTS[ind]
    key = 4096
    while key < 65537:
        BACKGROUND_COLOR_DICT[key] = palette[key]
        key *= 2
    
def main():
    print(BACKGROUND_COLOR_DICT)
    switch_cell_palette()
    print("-----------------")
    print(BACKGROUND_COLOR_DICT)

