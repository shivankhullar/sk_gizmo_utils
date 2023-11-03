#!/usr/bin/env python
"""
gizmo_setup.py: "Setup things in the gizmo code"

Usage: snapshot_timing.py [options]

Options:
    -h, --help                  Show this screen
    --repo_dir=<output>         Path to repository [default: ./]
    --systype=<systype>         System type [default: CITA_starq]
"""

import subprocess
from docopt import docopt

def modify_makefile_systype(path, systype):
    """
    Uncomment the whole makefile.systype file and add the systype
    Inputs:
        path: Path to the gizmo directory
        systype: System type to add to the makefile.systype file
    """

    file_name = "Makefile.systype"
    file_path = path+file_name
    if systype == "CITA_starq" or systype == "starq":
        systype = "CITA_starq"
    if systype == "Scinet_Niagara" or systype == "SciNet_Niagara" or \
        systype == "scinet_niagara" or systype =="Scinet" or systype == "scinet" or \
        systype == "Niagara" or systype == "niagara" or systype == "nia":
        systype = "Scinet_Niagara"
    if systype == "Frontera" or systype == "frontera":
        systype = "Frontera"
    try:
        with open(file_path, "r+") as file:
            lines = file.readlines()
            file.seek(0)
            file.truncate(0)  # Clear the file contents

            #Uncomment the line and write everything to file
            for line in lines:
                if not line.strip().startswith("#"):
                    line = "#" + line
                file.write(line)
            
            #Add the systype
            file.write(f'SYSTYPE="{systype}"\n')
            file.close()

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
    try:
        subprocess.run(["cp", f"{path}cooling/TREECOOL", f"{path}TREECOOL"], check=True)
    except:
        print(f"Error copying file {path}cooling/TREECOOL to {path}TREECOOL")
        exit(1)
    try:
        subprocess.run(["wget", f"-P {path}", "http://www.tapir.caltech.edu/~phopkins/public/spcool_tables.tgz"], check=True)
    except:
        print(f"Error downloading file http://www.tapir.caltech.edu/~phopkins/public/spcool_tables.tgz")
        exit(1)
    try:
        subprocess.run(["tar", "-xzvf", f"{path}spcool_tables.tgz", "-C", f"{path}spcool_tables"], check=True)
    except:
        print(f"Error extracting file {path}spcool_tables.tgz")
        exit(1)
    try:
        subprocess.run(["rm", "-rf", f"{path}spcool_tables.tgz"], check=True)
    except:
        print(f"Error removing file {path}spcool_tables.tgz")
        exit(1)

    return

def copy_job_submission_scripts(path, systype):
    """
    Copy job submission scripts to the gizmo directory
    Inputs:
        path: Path to the gizmo directory
        systype: System type to add to the makefile.systype file
    """
    if systype == "CITA_starq" or systype == "starq":
        try:
            subprocess.run(["cp", f"./job_scripts/CITA_starq/*", f"{path}"], check=True)
        except:
            print(f"Error copying job submission scripts to {path}")
            exit(1)
    elif systype == "Scinet_Niagara" or systype == "SciNet_Niagara" or \
        systype == "scinet_niagara" or systype =="Scinet" or systype == "scinet" or \
        systype == "Niagara" or systype == "niagara" or systype == "nia":
        try:
            subprocess.run(["cp", f"{path}gizmo_perf/sk_gizmo_utils/scripts/job_submission_scripts/Scinet_Niagara/*", f"{path}"], check=True)
        except:
            print(f"Error copying job submission scripts to {path}")
            exit(1)
    elif systype == "Frontera" or systype == "frontera":
        try:
            subprocess.run(["cp", f"{path}gizmo_perf/sk_gizmo_utils/scripts/job_submission_scripts/Frontera/*", f"{path}"], check=True)
        except:
            print(f"Error copying job submission scripts to {path}")
            exit(1)
    else:
        print(f"Error: systype {systype} not recognized")
        exit(1)

    return

if __name__ == '__main__':
    args = docopt(__doc__)
    repo_dir = args['--repo_dir']
    if repo_dir[-1] != "/":
        repo_dir += "/"
    systype = args['--systype']
    
    #Uncomment out the whole makefile.systype file and add the systype
    modify_makefile_systype(repo_dir, systype)
    #Copy job submissions scripts to the gizmo directory
    copy_job_submission_scripts(repo_dir)
    #Copy the TREECOOL file and download the spcool_tables
    setup_cooling_tables(repo_dir)
    print("Setup completed.")