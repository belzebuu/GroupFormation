#! /usr/bin/python

from optparse import OptionParser
#from matrix import *
#from dfs_example import dfs
import os
from time import *
import sys
from load_data import *
from utils import *
from models_ip import *
from models_ip_scip import *
from models_ip_weighted import *
from check_sol import *


from subprocess import *

# sys.path.append("../tags/PA2013/src/")
from lottery import *
from models_ip_instability import *
from models_ip_envyfree import *
from models_hooker import *


def main():

    usage = "usage: %prog [options] DIRNAME"
    parser = OptionParser(usage)
    parser.add_option("-a", "--allsol", action="store_true", dest="allsol", default=False,
                      help="All solutions")
    parser.add_option("-i", "--instability", action="store_false", dest="instability", default=True, help="Whether the constraint on instability should be included or not [default: %default]")
    parser.add_option("-g", "--groups", dest="groups", type="string", default="post", metavar="[pre|post]", help="Whether groups are formed pre or post [default: %default]")
    parser.add_option("-w", "--Wmethod", dest="Wmethod", type="string", default="owa", metavar="[identity|owa|powers]",
                      help="The weighting scheme, eg, \"owa\". [default: %default]")
    # parser.add_option("-n","--number", dest="number", type="int", default=10, metavar="NUMBER",
    #                  help="How many tasks/exercises [default: %default]")
    (options, args) = parser.parse_args()  # by default it uses sys.argv[1:]

    if not len(args) == 1:
        parser.error("Directory missing")

    dirname = args[0]
    problem = Problem(dirname)

    model = "minimax"

    minimax, solutions = model_ip(problem, options)
    stat = check_sol(solutions, problem, soldirname="sln")

    for st in stat:
        log = ['x']+[model]+solutions[0].solved+[os.path.basename(dirname)]+st
        print('%s' % ' '.join(map(str, log)))

    if options.Wmethod not in ["identity", "owa", "powers"]:
        sys.exit("Wmethod not recognized")

    start = clock()
    model = "minimax_instab_weighted"
    model = model+"-"+options.Wmethod
    value, solutions = model_ip_weighted(problem, options, minimax)

    elapsed = (clock() - start)

    stat = check_sol(solutions, problem, soldirname="sln")
    for st in stat:
        log = ['x']+[model]+[elapsed]+[os.path.basename(dirname)]+st
        print('%s' % ' '.join(map(str, log)))

# print '%s' % ' '.join(map(str, solutions[0].solved))


if __name__ == "__main__":
    main()
