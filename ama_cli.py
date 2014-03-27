import sys, chunker, requester
from optparse import OptionParser

parser = OptionParser(usage = "usage: %prog filename")

if __name__ == "__main__":
	if len(sys.arg) < 2:
		parser.print_help()
		sys.exit()
	
	requester = requester.Requester()
	chunker = chunker.Chunker(requester)
	
	chunker.process_file(sys.arg[1])