#!/usr/bin/env python2.7

"""
Parser for the outputs of 'batchload' script. 

Can take a list of batch outputs as inputs, by default takes all dq3batch*
in the current directory. 

The output is intended to be piped into 'batchload', so that restarting
unfinished downloads is simple: 

>>> batchcheck | batchload
"""

import argparse, sys, os
from glob import glob
from itertools import islice
from sys import stderr, stdout

def get_args(raw_args): 
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('batch_outputs', nargs='*')
    parser.add_argument('-v','--verbose', action='store_true')
    parser.add_argument('-c','--clean', action='store_true', 
                        help='remove old batch files')
    args = parser.parse_args(raw_args)
    return args

def run(): 
    args = get_args(sys.argv[1:])
    if not args.batch_outputs: 
        args.batch_outputs = glob('dq2batch-*.sh.o*')

    all_batch_out = args.batch_outputs
    batch_out = get_most_recent_batch(all_batch_out)
    if args.clean: 
        old_batch_files = set(all_batch_out) - set(batch_out)
        for old_file in old_batch_files: 
            os.remove(old_file)

    download_results = sorted(get_ds_and_result(x) for x in batch_out)
    for ds_name, results in download_results: 
        try: 
            n_failed = results['failed']
        except KeyError: 
            stderr.write('WARNING: {} missing summary\n'.format(
                    results['script']))
            if args.verbose: 
                _dump_tail(results)
            n_failed = float('inf')
        if n_failed != 0: 
            stdout.write(ds_name + '\n')
            if args.verbose: 
                stderr.write('-- {} --\n'.format(ds_name))
                _dump_tail(results)
    
def _dump_tail(job_summary_dict, stream=stderr): 
    stream.write('tail of: {}\n'.format(job_summary_dict['script']))
    for line in job_summary_dict['tail']: 
        if not line.strip(): 
            continue
        stream.write(line)
    stream.write('\n')

# here be parsing of dq2 output files
_ds_start_string = 'Querying DQ2 central catalogues to resolve datasetname'
_ds_failed_string = 'Number of failed file download attempts:'
def get_ds_and_result(output_name): 
    with open(output_name) as batch_file: 
        dataset_name = _get_dataset(batch_file)
        summary = _get_download_summary(batch_file)
        summary['script'] = output_name
    return dataset_name, summary 

def get_most_recent_batch(batch_files): 
    """
    Filter batch output files, taking the only the most recent that apply 
    to a given dataset. 
    """
    most_recent_batch_num = {}
    script_name = {}
    for f in batch_files: 
        batch_number = int(f.split('o')[-1])
        with open(f) as batch_out: 
            ds_name = _get_dataset(batch_out)
        ds_max_so_far = most_recent_batch_num.get(ds_name,0)
        if ds_max_so_far < batch_number: 
            most_recent_batch_num[ds_name] = batch_number
            script_name[ds_name] = f
    return script_name.values()


def _get_dataset(output_file): 
    dataset_name = ''
    output_file.seek(0)
    for line in islice(output_file, 10): 
        if line.startswith(_ds_start_string): 
            ds_name = line.split()[-1].strip()
            return ds_name
    raise IOError('no dataset name found')

def _get_download_summary(output_file): 
    output_file.seek(0,2) # go to end
    end_pos = output_file.tell()

    # last 2k or so bytes are all we need
    aprox_tail_position = max(end_pos - 4000, 0) 
    output_file.seek(aprox_tail_position)
    lines = output_file.readlines()[-10:]
    summary = {}
    for line in lines: 
        if line.startswith(_ds_failed_string): 
            summary['failed'] = int(line.split()[-1])

    summary['tail'] = lines
    return summary


if __name__ == '__main__': 
    run()
