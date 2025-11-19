import argparse
import time
import subprocess
import pandas as pd
import os
import sys

"""
Functional profiler for a metagenome sample. The profiler will work with a FracMinHash sketch of KOs,
 and a metagenome sample. The profiler needs to know which parameters were used to obtain the 
 KO sketch (protein kmer size, and scaled -- see sourmash documentations for more details about these parameters)
"""
def parse_args():
    # create parser
    parser = argparse.ArgumentParser(description="Functional profiler for a metagenome sample. The profiler will work with a FracMinHash sketch of KOs, and a metagenome sample. The profiler needs to know which parameters were used to obtain the KO sketch (protein kmer size, and scaled -- see sourmash documentations for more details)")
    
    # required arguments
    parser.add_argument("mg_filename", type=str, help="Name of the metagenome file")
    parser.add_argument("ko_sketch", type=str, help="Filename of KO sketch")
    parser.add_argument("ksize", type=int, help="Protein kmer size (7, 11, or 15) used to obtain the KO sketch")
    parser.add_argument("scaled", type=int, help="The scaled parameter used to obtain the KO sketch")
    parser.add_argument("output", type=str, help="Output filename, where the KO profiles will be written")
    
    # optional arguments
    parser.add_argument('-t', "--threshold_bp", type=int, help="The threshold_bp to run sourmash gather (1000 is preferred)", default=1000)
    parser.add_argument('-p', "--prefetch_file", type=str, help="The sourmash prefetch output")
    
    # parse arguments
    args = parser.parse_args()
    return args

"""
Sanity check the environment. 
"""
def sanity_check():
    # check if sourmash is installed
    found_error = False
    try:
        res = subprocess.call( ['sourmash', '--help'] )
    except:
        print('Error: sourmash is not installed. Please install sourmash before running this script.')
        found_error = True

    # check if pandas is installed
    try:
        import pandas as pd
    except ImportError:
        print('Error: pandas is not installed. Please install pandas before running this script.')
        found_error = True

    # check if numpy is installed
    try:
        import numpy as np
    except ImportError:
        print('Error: numpy is not installed. Please install numpy before running this script.')
        found_error = True

    if found_error:
        sys.exit(1)

"""
Check the arguments for correctness.
"""
def check_args(args):
    # check if the metagenome file exists
    if not os.path.exists(args.mg_filename):
        print(f'Error: Metagenome file {args.mg_filename} does not exist. Exiting...')
        sys.exit(1)

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


"""
Create a sketch of the metagenome sample. Returns the filename of the sketch.
"""
def create_sketch(mg_filename, ksize, scaled):
    print('Creating metagenome sketch...')
    metagenome_sketch_filename = f'{mg_filename}_sketch_{int(time.time())}.sig.zip'

    # make sure that write permission is available on sketch filename
    if os.path.exists(metagenome_sketch_filename):
        print(f'{metagenome_sketch_filename} already exists. Please provide a new filename.')
        sys.exit(1)

    # generate command and execute
    cmd = f'sourmash sketch translate -p scaled={scaled},k={ksize},abund {mg_filename} -o {metagenome_sketch_filename}'
    
    # execute command and check for errors
    res = subprocess.call( cmd.split(' ') )
    if res != 0:
        print(f'Error: Failed to create sketch of the metagenome. Exiting...')
        sys.exit(1)

    # assert that the sketch file has been created
    if not os.path.exists(metagenome_sketch_filename):
        print(f'Error: Failed to create sketch of the metagenome. Exiting...')
        sys.exit(1)

    print(f'Sketch of the metagenome has been saved to {metagenome_sketch_filename}')

    return metagenome_sketch_filename

    
def main():
    # sanity check the environment
    sanity_check()

    # parse arguments
    args = parse_args()

    # check arguments
    check_args(args)

    # extract arguments
    mg_filename = args.mg_filename
    ko_sketch = args.ko_sketch
    ksize = args.ksize
    scaled = args.scaled
    output_filename = args.output
    threshold_bp = args.threshold_bp
    prefetch_output_filename = args.prefetch_file

    # create metagenome sketch
    metagenome_sketch_filename = create_sketch(mg_filename, ksize, scaled)

    # run sourmash prefetch
    if prefetch_output_filename is None:
        prefetch_output_filename = f'{mg_filename}_gather_{int(time.time())}.tmp'
    print('Running sourmash prefetch...')
    # command: sourmash prefetch <mg_sketch_name> <ko_sketch_name> -o <prefetch_output_filename> -k <ksize> --scaled <scaled> --protein --threshold-bp <threshold_bp>
    cmd = f'sourmash prefetch {metagenome_sketch_filename} {ko_sketch} -o {prefetch_output_filename} -k {ksize} --scaled {scaled} --protein' + f' --threshold-bp {threshold_bp}'
    print(cmd)
    subprocess.call( cmd.split(' ') )
    print(f'sourmash prefetch results have been stored to {prefetch_output_filename}')
    
    # check if file is empty
    if os.path.exists(prefetch_output_filename) and os.stat(prefetch_output_filename).st_size > 0:
        # extract ko info from prefetch output
        print('Extracting KO abundances from prefetch output...')
        df = pd.read_csv(prefetch_output_filename, delimiter=',')
        df_new = df[ ['match_name', 'f_match_query'] ]
        sum_weights = df_new['f_match_query'].sum(axis=0)
        df_tmp = df_new['f_match_query'].divide(sum_weights)
        df_out = pd.concat([df['match_name'], df_tmp], axis=1)
        df_out.columns = ['ko_id', 'abundance']
        df_out.to_csv(output_filename, index=False)
        print(f'KO profiles have been written to {output_filename}')
    else:
        print('Prefetch output file is empty. No matches in KEGG KOs found. Creating an empty KO profile CSV')
        df_out = pd.DataFrame(columns=['ko_id', 'abundance'])
        df_out.to_csv(output_filename, index=False)

    # remove tmps
    # print('Removing temps...')
    # subprocess.call( ['rm', metagenome_sketch_filename] )
    print('Exiting...')

