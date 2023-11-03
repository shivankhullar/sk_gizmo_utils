#!/usr/bin/env python
"""
clone_gizmo.py: "Clone repositories related to the gizmo code"

Usage: snapshot_timing.py [options]

Options:
    -h, --help                  Show this screen
"""

import numpy as np
from git import Repo


def clone_repo()

if __name__ == '__main__':
    args = docopt(__doc__)
    snapdir = args['--snapdir']
    output_dir = args['--output_dir']
    start_a = float(args['--start_a'])
    end_a = float(args['--end_a'])
    spacing = convert_to_array(args['--spacing']) 
    cut_off_time = float(args['--cut_off_time'])
    key = args['--key']
    co = get_cosomology()
    
    end_time = args['--end_time']
    if end_time!='None':
        end_time = float(end_time) + float(co.t_from_a(start_a))/Myr
        end_a = np.round(float(co.a_from_t(end_time*Myr)), 7)

    
    _ = get_scale_factors(co, start_a, end_a, spacing, cut_off_time, key=key, output=output_dir)
    print ('Done!')


Repo.clone_from(git_url, repo_dir)
