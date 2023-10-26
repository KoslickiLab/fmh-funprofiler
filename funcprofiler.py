import argparse
import time
import subprocess
import pandas as pd


def main():
    parser = argparse.ArgumentParser(description="Functional profiler for a metagenome sample. The profiler will work with a FracMinHash sketch of KOs, and a metagenome sample. The profiler needs to know which parameters were used to obtain the KO sketch (protein kmer size, and scaled -- see sourmash documentations for more details)")
    parser.add_argument("mg_filename", type=str, help="Name of the metagenome file")
    parser.add_argument("ko_sketch", type=str, help="Filename of KO sketch")
    parser.add_argument("ksize", type=int, help="Protein kmer size (7, 11, or 15) used to obtain the KO sketch", default=15)
    parser.add_argument("scaled", type=int, help="The scaled parameter used to obtain the KO sketch", default=1000)
    parser.add_argument("threshold_bp", type=int, help="The threshold_bp to run sourmash gather (1000 is preferred)", default=1000)
    parser.add_argument("output", type=str, help="Output filename, where the KO profiles will be written")
    args = parser.parse_args()

    mg_filename = args.mg_filename
    ko_sketch = args.ko_sketch
    ksize = args.ksize
    scaled = args.scaled
    output_filename = args.output
    threshold_bp = args.threshold_bp

    print('Creating metagenome sketch...')
    metagenome_sketch_filename = f'{mg_filename}_sketch_{int(time.time())}.tmp'
    cmd = f'sourmash sketch translate -p scaled={scaled},k={ksize} {mg_filename} -o {metagenome_sketch_filename}'
    subprocess.call( cmd.split(' ') )
    print(f'Sketch of the metagenome has been saved to {metagenome_sketch_filename}')

    # run gather
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
    df_out.to_csv(output_filename)
    print(f'KO profiles have been written to {output_filename}')

    # remove tmps
    print('Removing temps...')
    subprocess.call( ['rm', metagenome_sketch_filename, gather_output_filename] )
    print('Exiting...')


if __name__ == '__main__':
    main()
