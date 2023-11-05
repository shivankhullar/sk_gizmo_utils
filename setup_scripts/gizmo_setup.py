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
        systype = "Scinet_Niagara"
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
    elif systype == "Scinet_Niagara" ":
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



    file_name = "Makefile"
    file_path = path+file_name
    
    # Paths to the source and destination files
    source_file_path = "./system_setup_scripts/CITA_starq/System_makefile.txt"
    destination_file_path = "destination.txt"

    # Line number where you want to insert the contents
    insert_line_number = 3  # Change this to the desired line number

    # Read the contents from the source file
    with open(source_file_path, "r") as source_file:
        source_contents = source_file.readlines()

    # Insert the contents into the destination file at the specified line number
    with open(destination_file_path, "r") as destination_file:
        destination_contents = destination_file.readlines()

    destination_contents = (
        destination_contents[:insert_line_number - 1]
        + source_contents
        + destination_contents[insert_line_number - 1 :]
    )

    # Write the modified contents back to the destination file
    with open(destination_file_path, "w") as destination_file:
        destination_file.writelines(destination_contents)

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