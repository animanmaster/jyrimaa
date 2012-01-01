#!/usr/bin/env python
import sys

###############CONFIG###################################

COLUMNS_TO_KEEP = [0, 1, 2, 9, 10, 13, 14, 21, 22, 26]
FILENAME = "relevant_game_data.tab"
APPEND = False

#########################################################

def process(gamefile, outfile):
    # yay SO: http://stackoverflow.com/questions/4796764/read-file-from-line-2-or-skip-header-row
    last_col = COLUMNS_TO_KEEP[-1]
    with open(gamefile, 'r') as lines:
        next(lines) #skip first line
        for line in lines:
            data = line.split("\t")
            for col in COLUMNS_TO_KEEP:
                outfile.write(data[col] + ("\t" if col != last_col else ""))
            outfile.write("\n")
            outfile.flush()

def main():
    outfile = open(FILENAME, "a" if APPEND else "w")
    for arg in sys.argv[1:]:
        print "Processing", arg
        process(arg, outfile)
    print "Generated", FILENAME

if __name__ == "__main__":
    main()

