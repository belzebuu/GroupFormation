#! /usr/bin/python

import argparse
import os
from time import *
import sys
from prensio.load_data import *
from prensio.utils import *
from prensio.models_ip_ext import *
from prensio.check_sol import *
from pathlib import Path

from subprocess import *
import textwrap


def main():
    s = textwrap.dedent("""\
                        Example:
                        python3 src/main.py -m data/example/ | tee log.txt
                        """)
    parser = argparse.ArgumentParser(description='Exam scheduler.', epilog=s)
    parser.add_argument("-m", "--disallow_merging_groups", dest="disallow_merging_groups", action='store_true', help="To disallow merging of pre-made groups in teams [default: %(default)s]")
    parser.add_argument("-t", "--time_limit", dest="time_limit", action='store', type=int, default=100, help="Time limit [default: %(default)s]")
    parser.add_argument('-l','--log_dir', metavar='logdir', dest='logdirname', type=Path,
                        action='store', nargs=1, required=False, default=Path.cwd()/"log",
                        help='the name of the directory where to put log files. It checks for existance. [default: %(default)s]')
    parser.add_argument("-x", "--latex", dest="latex", action='store_true', help="Include LaTeX output [default: %(default)s]")   
    parser.add_argument('-s','--sol_dir', metavar='soldir', dest='soldirname', type=str,
                        action='store', nargs=1, required=False, default="sln",
                        help='the name of the directory where to put solution files. It checks for existance. [default: %(default)s]')
    parser.add_argument("input_directory", help="The directory of the input data", type=str)
    args = parser.parse_args()

    if not os.path.exists(args.logdirname):
        os.makedirs(args.logdirname, mode = 0o777)
    if not os.path.exists(args.soldirname):
        os.makedirs(args.soldirname, mode = 0o777)

    problem = Problem(args.input_directory)

    solutions = model_ip_ext(problem, args.disallow_merging_groups, args.logdirname, args.time_limit)
    stat = check_all_sols(solutions, problem, soldirname=args.soldirname, latex=args.latex)

    model = "discrepancy"
    for st in stat:
        log = ['x']+[model]+solutions[0].solved+[os.path.basename(args.input_directory)]+st
        print('%s' % ' '.join(map(str, log)))



if __name__ == "__main__":
    main()
