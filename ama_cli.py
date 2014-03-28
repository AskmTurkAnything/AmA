import sys, chunker, requester
from optparse import OptionParser

parser = OptionParser(usage = "usage: %prog filename")
parser.add_option("-a", "--max_assignments", action = "store", type = "string", dest = "max_assignments")
parser.add_option("-c", "--cost", action = "store", type = "float", dest = "cost")
parser.add_option("-t", "--tags", action = "store", type = "string", dest = "tags")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        parser.print_help()
        sys.exit()

    (options, args) = parser.parse_args()

    requester = requester.Requester()
    chunker = chunker.Chunker(requester)

    chunker.process_file(sys.argv[1], options.max_assignments, options.cost, options.tags)
