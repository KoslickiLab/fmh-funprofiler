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
    parser.add_argument('-g', "--gather_file", type=str, help="The sourmash gather output")
    
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
Create a sketch of the metagenome sample. Returns the filename of the sketch.
"""
def create_sketch(mg_filename, ksize, scaled):
    print('Creating metagenome sketch...')
    metagenome_sketch_filename = f'{mg_filename}_sketch_{int(time.time())}.tmp'

    # make sure that write permission is available on sketch filename
    if os.path.exists(metagenome_sketch_filename):
        print(f'{metagenome_sketch_filename} already exists. Please provide a new filename.')
        sys.exit(1)

    # generate command and execute
    cmd = f'sourmash sketch translate -p scaled={scaled},k={ksize} {mg_filename} -o {metagenome_sketch_filename}'
    
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

    # extract arguments
    mg_filename = args.mg_filename
    ko_sketch = args.ko_sketch
    ksize = args.ksize
    scaled = args.scaled
    output_filename = args.output
    threshold_bp = args.threshold_bp
    gather_output_filename = args.gather_file

    # create metagenome sketch
    metagenome_sketch_filename = create_sketch(mg_filename, ksize, scaled)

    # run gather
    if gather_output_filename is None:
        gather_output_filename = f'{mg_filename}_gather_{int(time.time())}.tmp'
    print('Running sourmash gather...')
    cmd = f'sourmash gather --protein -k {ksize} --estimate-ani-ci --threshold-bp {threshold_bp} ' + metagenome_sketch_filename + ' ' + ko_sketch + ' -o ' + gather_output_filename
    subprocess.call( cmd.split(' ') )
    print(f'sourmash gather results have been stored to {gather_output_filename}')

    # extract ko info from gather output
    print('Extracting KO abundances from gather output...')
    df = pd.read_csv(gather_output_filename, delimiter=',')
    df_new = df[ ['name', 'f_unique_weighted'] ]
    sum_weights = df_new['f_unique_weighted'].sum(axis=0)
    df_tmp = df_new['f_unique_weighted'].divide(sum_weights)
    df_out = pd.concat([df['name'], df_tmp], axis=1)
    df_out.columns = ['ko_id', 'abundance']
    df_out.to_csv(output_filename, index=False)
    print(f'KO profiles have been written to {output_filename}')

    # remove tmps
    print('Removing temps...')
    subprocess.call( ['rm', metagenome_sketch_filename] )
    print('Exiting...')


if __name__ == '__main__':
    main()
