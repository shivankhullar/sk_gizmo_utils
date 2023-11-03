#!/usr/bin/env python
"""
clone_gizmo.py: "Clone repositories related to the gizmo code"

Usage: snapshot_timing.py [options]

Options:
    -h, --help                  Show this screen
    --repo_name=<repo_name>     Name of the repository to clone [default: gizmo_imf_sk]
    --dest_dir=<output>         Destination directory [default: ./]
"""

import subprocess
from docopt import docopt


def clone_repo(repo_url, destination_dir):
    """
    Clone a GitHub repository using the 'git' command.
    
    Inputs:
        repo_url: URL of the repository to clone
        destination_dir: Directory where the repository will be cloned
    """
    repo_name = repo_url.split("/")[-1].split(".git")[0]

    # Clone the repository using the 'git' command
    clone_command = ["git", "clone", repo_url, f"{destination_dir}/{repo_name}"]

    try:
        subprocess.run(clone_command, check=True)
        print(f"Cloned {repo_name} successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Error cloning {repo_name}: {e}")

    print("Cloning completed.")
    return

def get_repo_url(repo_name):
    """
    Get the URL of the repository to clone.
    Inputs:
        repo_name: Name of the repository to clone
    """
    if repo == "gizmo_imf_sk" or repo=="imf" or repo=="sfire":
        repo_url = "git@bitbucket.org:shivankhullar/gizmo_imf_sk.git"
    
    elif repo == "gizmo_public" or repo=="public":
        repo_url = "git@bitbucket.org:phopkins/gizmo-public.git"
    
    else:
        print("Invalid repo name. Exiting...")
        exit(1)

    return repo_url

if __name__ == '__main__':
    args = docopt(__doc__)
    dest_dir = args['--dest_dir']
    repo = args['--repo_name']
    repo_url = get_repo_url(repo)
    clone_repo(repo_url, dest_dir)
