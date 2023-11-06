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

def get_system_type(systype):
    if systype == "CITA_starq" or systype == "starq":
        systype = "CITA_starq"
    if systype == "Scinet_Niagara" or systype == "SciNet_Niagara" or \
        systype == "scinet_niagara" or systype =="Scinet" or systype == "scinet" or \
        systype == "Niagara" or systype == "niagara" or systype == "nia":
        systype = "SciNet"
    if systype == "Frontera" or systype == "frontera" or systype == "front":
        systype = "Frontera"

    return systype

def modify_makefile_systype(path, systype):
    """
    Uncomment the whole makefile.systype file and add the systype
    Inputs:
        path: Path to the gizmo directory
        systype: System type to add to the makefile.systype file
    """

    file_name = "Makefile.systype"
    file_path = path+file_name
    try:
        with open(file_path, "r+") as file:
            lines = file.readlines()
            for line in lines:
                if not line.strip().startswith("#"):
                    #Check if it corresponds to the systype
                    if systype in line:
                        #Exit the function if the systype already exists and is uncommented
                        print (f"System type {systype} already exists in Makefile.systype file. Leaving Makefile.systype file unchanged...")
                        return

            #lines = file.readlines()
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
        subprocess.run(["wget", "-P", f"{path}", "http://www.tapir.caltech.edu/~phopkins/public/spcool_tables.tgz"], check=True)
    except:
        print(f"Error downloading file http://www.tapir.caltech.edu/~phopkins/public/spcool_tables.tgz")
        exit(1)
    try:
        subprocess.run(["tar", "-xzvf", f"{path}spcool_tables.tgz", "-C", f"{path}"], check=True)
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
    if systype == "CITA_starq":
        try:
            subprocess.Popen([f"cp ./system_setup_scripts/CITA_starq/* {path}"], shell=True, stdout=subprocess.PIPE,
                                    stderr=subprocess.PIPE)
        except:
            print(f"Error copying job submission scripts to {path}")
            exit(1)
    elif systype == "Scinet_Niagara":
        try:
            subprocess.Popen([f"cp ./system_setup_scripts/Niagara/* {path}"], shell=True, stdout=subprocess.PIPE,
                                    stderr=subprocess.PIPE)
        except:
            print(f"Error copying job submission scripts to {path}")
            exit(1)
    elif systype == "Frontera":
        try:
            subprocess.Popen([f"cp ./system_setup_scripts/Frontera/* {path}"], shell=True, stdout=subprocess.PIPE,
                                    stderr=subprocess.PIPE)
        except:
            print(f"Error copying job submission scripts to {path}")
            exit(1)
    else:
        print(f"Error: systype {systype} not recognized")
        exit(1)

    return

def modify_makefile(path, systype):
    """
    Modify makefile for the system type
    Inputs:
        path: Path to the gizmo directory
        systype: System name
    """
    if systype == "CITA_starq":
    # Paths to the source and destination files
        source_file_path = "./system_setup_scripts/CITA_starq/System_makefile.txt"
    if systype == "Scinet_Niagara":
        source_file_path = "./system_setup_scripts/Niagara/System_makefile.txt"
    if systype == "Frontera":
        source_file_path = "./system_setup_scripts/Frontera/System_makefile.txt"


    first_file_path = path+"Makefile"     #Path to the destination file
    second_file_path = source_file_path   #Path to the source file

    # Line number where you want to insert the contents if they don't match
    insert_line_number = 84  # Change this to the desired line number

    # Read the contents of the second (small) file
    with open(second_file_path, "r") as second_file:
        second_contents = second_file.readlines()

    # Open the first (large) file in read mode
    with open(first_file_path, "r") as first_file:
        first_contents = first_file.readlines()

    # Check if the contents of the second file are contained within the first file
    contains_second_contents = all(line in first_contents for line in second_contents)

    if not contains_second_contents:
        # If the contents are not contained, insert them at the specified line
        first_contents[insert_line_number - 1:insert_line_number - 1] = second_contents

        # Write the modified contents back to the first (large) file
        with open(first_file_path, "w") as first_file:
            first_file.writelines(first_contents)

        print("System specific Makefile contents inserted into the Makefile at line", insert_line_number)
    else:
        print("Makefile's contents are sufficient.")

    print("Check and insert completed.")
    return


if __name__ == '__main__':
    args = docopt(__doc__)
    repo_dir = args['--repo_dir']
    if repo_dir[-1] != "/":
        repo_dir += "/"
    systype = args['--systype']
    
    #Get the system type
    systype = get_system_type(systype)
    
    #Uncomment out the whole makefile.systype file and add the systype
    print ('Modifying makefile.systype file...')
    modify_makefile_systype(repo_dir, systype)
    
    #Modify makefile for the system type
    print ('Modifying makefile file...')
    modify_makefile(repo_dir, systype)
    
    #Copy the TREECOOL file and download the spcool_tables
    print ('Setting up cooling tables...')
    setup_cooling_tables(repo_dir)

    #Copy job submissions and module load scripts to the gizmo directory
    print ('Copying job submission scripts...')
    copy_job_submission_scripts(repo_dir, systype)

    print("Setup completed.")