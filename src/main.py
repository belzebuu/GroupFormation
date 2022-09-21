#! /usr/bin/python

import argparse
import os
from time import *
import sys
from load_data import *
from utils import *
from models_ip_ext import *
from check_sol import *

from subprocess import *
import textwrap


def main():
    s = textwrap.dedent("""\
                        Example:
                        python3 src/main.py -g post data/private/zhiru-e22-ds830/ | tee log.txt
                        """)
    parser = argparse.ArgumentParser(description='Exam scheduler.', epilog=s)
    parser.add_argument("-m", "--merge_groups", dest="merging_groups", action='store_true', help="To allow merging of groups in teams [default: %default]")
    parser.add_argument('-l','--log_dir', metavar='LogDir', dest='logdirname', type=str,
                        action='store', nargs=1, required=False, default="log",
                        help='the name of the directory where to put log files. It checks for existance. [default: %default]')
    parser.add_argument('-s','--sol_dir', metavar='SolDir', dest='soldirname', type=str,
                        action='store', nargs=1, required=False, default="sln",
                        help='the name of the directory where to put solution files. It checks for existance. [default: %default]')
    parser.add_argument("input_directory", help="The directory of the input data",type=str)
    args = parser.parse_args()


    problem = Problem(args.input_directory)

    solutions = model_ip_ext(problem, args.merging_groups)
    stat = check_all_sols(solutions, problem, soldirname="sln")

    model = "discrepancy"
    for st in stat:
        log = ['x']+[model]+solutions[0].solved+[os.path.basename(args.input_directory)]+st
        print('%s' % ' '.join(map(str, log)))



if __name__ == "__main__":
    main()
