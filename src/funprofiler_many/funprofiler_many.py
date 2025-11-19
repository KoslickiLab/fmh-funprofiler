"""
This script takes the following inputs:
1. KO sketch file name
2. ksize (protein)
3. scaled parameter
4. a text file, that is a csv file, containing two columns: metagenome file name and output file name
5. threshold_bp

This script does the following:
1. Check if arguments are valid
2. For every pair in the text file, it invokes funcprofiler.py with the following arguments:
    a. KO sketch file name
    b. ksize
    c. scaled parameter
    d. metagenome file name
    e. output file name
    f. threshold_bp

All instances of funcprofiler.py are run in parallel.
"""

import os
import sys
import subprocess
import argparse
from multiprocessing import Process
import pandas as pd

def parse_arguments():
    parser = argparse.ArgumentParser(description='Run funcprofiler.py on multiple metagenomes in parallel.')
    parser.add_argument('ko_sketch', type=str, help='KO sketch file name')
    parser.add_argument('ksize', type=int, help='ksize (protein)')
    parser.add_argument('scaled', type=int, help='scaled parameter')
    parser.add_argument('filelist', type=str, help='Text file containing metagenome file names and output file names')
    parser.add_argument('threshold_bp', type=int, help='threshold_bp')
    return parser.parse_args()

def check_args(args):
    # check if the KO sketch file exists
    if not os.path.exists(args.ko_sketch):
        print(f'Error: KO sketch file {args.ko_sketch} does not exist. Exiting...')
        sys.exit(1)

    # check if the protein kmer size is valid
    if args.ksize not in [7, 11, 15]:
        print(f'Error: Protein kmer size {args.ksize} is not valid. Exiting...')
        sys.exit(1)

    # check if the scaled parameter is valid
    if args.scaled < 1:
        print(f'Error: Scaled parameter {args.scaled} is not valid. Exiting...')
        sys.exit(1)

    # check if the threshold_bp is valid
    if args.threshold_bp < 1:
        print(f'Error: threshold_bp {args.threshold_bp} is not valid. Exiting...')
        sys.exit(1)

    return True


def run_funcprofiler(metagenome_filename, output_filename, ko_sketch_filename, ksize, scaled, threshold_bp):
    # run funcprofiler.py. Command: python funcprofiler.py <metagenome_filename> <ko_sketch_filename> <ksize> <scaled> <output_filename> -t <threshold_bp>

    # find the directory that this (currently running) script is in
    script_dir = os.path.dirname(os.path.realpath(__file__))

    try:
        subprocess.run(['python', os.path.join(script_dir, 'funcprofiler.py'), metagenome_filename, ko_sketch_filename, str(ksize), str(scaled), output_filename, '-t', str(threshold_bp)], check=True)
    except subprocess.CalledProcessError as e:
        print(f'Error: funcprofiler.py failed with error code {e.returncode}. Exiting...')
        sys.exit(1)
    return None

def main():
    args = parse_arguments()
    if check_args(args):
        # read the filelist
        filelist = pd.read_csv(args.filelist, sep=',', header=None, names=['metagenome_filename', 'output_filename'])

        # run funcprofiler.py on each pair of metagenome_filename and output_filename
        process_lit = []
        for index, row in filelist.iterrows():
            p = Process(target=run_funcprofiler, args=(str(row['metagenome_filename']), str(row['output_filename']), args.ko_sketch, args.ksize, args.scaled, args.threshold_bp))
            process_lit.append(p)

        for p in process_lit:
            p.start()

        for p in process_lit:
            p.join()

