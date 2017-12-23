######################################################
#
#    scrape_raw_list.py
#
#  Scrapes Pokemon stats for Gamepress.
#  Takes a complete copy of the entire text of
#  https://pokemongo.gamepress.gg/pokemon-list
#  as input and dumps stats as JSON.
#
######################################################

import sys
import optparse

def main(argv=None):
    usage="Usage: scrape_raw_list.py <input.txt> <output.json>"
    parser = optparse.OptionParser(usage=usage)
    
    (options, args) = parser.parse_args()
    
    # Get arguments
    try:
        inputFileName, outputFileName = args
    except ValueError:
        print ("ERROR: Invalid number of arguments")
        print (usage)
        return 1
    
    # Load input file
    with open(inputFileName, "r") as f:
        lines = [line.strip() for line in f.readlines()]
    
    # Find region of interest
    begin = 0
    begin_pattern = "#	Pokemon	STA	ATK	DEF	CP	Rating"
    end = 0
    end_pattern = "Loading..."

    for i, line in enumerate(lines):
        if line == begin_pattern:
            print("beginning on line {0}".format(i + 1))
            begin = i + 1
        if line == end_pattern:
            print("donezo on line {0}".format(i))
            end = i
    
    # Parse each entry and write to output file
    with open(outputFileName, "w") as f:
        f.write("{\n")
        entries = []
        """
        # Each entry is 7 lines long.
        # Format:
        #   Species number
        #   Species name
        #   Base STA
        #   Base ATK
        #   Base DEF
        #   Max CP (ignored)
        #   Rating (ignored)
        for i in range(begin, end, 7):
            spec_num = int(lines[i])
            
            # species name
            j = i + 1
            name = lines[j].strip().lower()
            j += 1
            # stats [STA, ATK, DEF]
            stats = lines[j:j+3]
        """
        # Each entry is a single line, formatted as follows:
        # <species number> <something> <species name> <base STA> <base ATK> <base DEF> <max CP> <rating>
        for i in range(begin, end):
            splitline = lines[i].split()
            spec_num = int(splitline[0])
            name = splitline[-6].lower()
            stats = splitline[-5:-2]
            # Special cases for Nidorans since the
            # Unicode characters get lost in the scrape
            if spec_num == 29:
                name = "nidoranf"
            elif spec_num == 32:
                name = "nidoranm"
            entry = "    \"{0}\": [".format(name)
            
            entry += "{0}]".format(", ".join(stats))
            entries.append(entry)
        f.write(",\n".join(entries))
        f.write("\n}")

if __name__ == "__main__":
    sys.exit(main())
