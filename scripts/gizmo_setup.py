#!/usr/bin/env python
"""
gizmo_setup.py: "Setup things in the gizmo code"

Usage: snapshot_timing.py [options]

Options:
    -h, --help                  Show this screen
    --repo_dir=<output>         Path to repository [default: ./]
"""

import subprocess
from docopt import docopt

def uncomment_makefile_systype(path):
    """
    Uncomment the whole makefile.systype file
    Inputs:
        path: Path to the gizmo directory
    """

    file_name = "Makefile.systype"
    file_path = path+file_name
    try:
        with open(file_path, "r+") as file:
            lines = file.readlines()
            file.seek(0)
            file.truncate(0)  # Clear the file contents

            for line in lines:
                if not line.strip().startswith("#"):
                    line = "#" + line
                file.write(line)
    except:
        print(f"Error opening file {file_path}")
        exit(1)
    return

def setup_cooling_tables(path):
    """
    Copy the TREECOOL file and download the spcool_tables
    Inputs:
        path: Path to the gizmo directory
    """
    subprocess.run(["cp", f"{path}cooling/TREECOOL", f"{path}TREECOOL"], check=True)
    subprocess.run(["wget", f"-P {path}", "http://www.tapir.caltech.edu/~phopkins/public/spcool_tables.tgz"], check=True)
    subprocess.run(["tar", "-xzvf", f"{path}spcool_tables.tgz", "-C", f"{path}spcool_tables"], check=True)
    subprocess.run(["rm", "-rf", f"{path}spcool_tables.tgz"], check=True)
    return



if __name__ == '__main__':
    args = docopt(__doc__)
    repo_dir = args['--repo_dir']
    if repo_dir[-1] != "/":
        repo_dir += "/"
    
    #Uncomment out the whole makefile.systype file
    uncomment_makefile_systype(repo_dir)
    #Add the systype to makefile.systype

    #Copy the TREECOOL file and download the spcool_tables
    setup_cooling_tables(repo_dir)
    print("Setup completed.")