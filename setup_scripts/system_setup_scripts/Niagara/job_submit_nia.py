import subprocess
import os
from datetime import datetime
import argparse

def create_sbatch_script(job_number, param_file, restart, num_nodes, job_name, dependency=None, account=1, cores_per_node=40):
    """
    Generate content for an sbatch script for GIZMO simulation.

    Args:
        job_number: Number of the job in the sequence
        param_file: Parameter file for the GIZMO simulation
        restart: Integer indicating restart mode (1 or 2) or None for no flag
        num_nodes: Number of nodes requested
        job_name: Base name for the job
        dependency: Job ID this job depends on
        account: Account number (1 for rrg-matzner, 2 for rrg-murray-ac)
        cores_per_node: Number of cores per node (default: 40)

    Returns:
        String containing the sbatch script content
    """
    num_cores = num_nodes * cores_per_node

    # Map account number to account name
    account_map = {
        1: "rrg-matzner",
        2: "rrg-murray-ac"
    }
    account_name = account_map.get(account, "rrg-matzner")  # Default to rrg-matzner if invalid account number

    script = [
        "#!/bin/bash",
        f"#SBATCH --account={account_name}",
        f"#SBATCH --nodes={num_nodes}",
        f"#SBATCH --ntasks-per-node={cores_per_node}",
        "#SBATCH --time=23:00:00",
        f"#SBATCH --job-name={job_name}_{job_number}",
        "#SBATCH --output=mpi_output_%j.txt",
        "#SBATCH --mail-type=FAIL"
    ]

    if dependency:
        script.append(f"#SBATCH --dependency=afterany:{dependency}")

    script.extend([
        "",
        "cd $SLURM_SUBMIT_DIR",
        "cd ../",
        "",
        "module load intel intelmpi gsl hdf5 fftw",
        "",
        "date_today=\"$(date +'%d-%m-%Y')\"",
        "echo $date_today",
        "base_filename=\"shell_${date_today}\"",
        "date_filename=\"${base_filename}.out\"",
        "echo $date_filename",
        "",
        "counter=1",
        "filename=$date_filename",
        "",
        "while [[ -e $filename ]]; do",
        "    counter=$((counter + 1))",
        "    filename=\"${base_filename}_$counter.out\"",
        "    echo \"File exists, checking next: $filename\"",
        "done"
    ])

    if restart:
        script.extend([
            "",
            "module load python",
            "jargon",
            f"python prep_restart.py {param_file}",
            ""
        ])

    # Only include restart flag if specified
    mpirun_cmd = f"mpirun -np {num_cores} ./GIZMO {param_file}"
    if restart is not None:
        mpirun_cmd += f" {restart}"
    mpirun_cmd += " >\"$filename\""
    script.append(mpirun_cmd)

    return "\n".join(script)

def submit_job_chain(num_jobs, param_file, restart, num_nodes, job_name, initial_dependency=None, account=1, cores_per_node=40):
    """
    Submit a chain of dependent GIZMO simulation jobs to SLURM.

    Args:
        num_jobs: Number of jobs to submit in the chain
        param_file: Parameter file for the GIZMO simulation
        restart: Integer indicating restart mode (1 or 2) or None for no flag
        num_nodes: Number of nodes requested
        job_name: Base name for the job
        initial_dependency: Job ID that the first job in the chain should depend on
        account: Account number (1 for rrg-matzner, 2 for rrg-murray-ac)
        cores_per_node: Number of cores per node (default: 40)
    """
    previous_job_id = initial_dependency

    for job_num in range(1, num_jobs + 1):
        # Create script file with timestamp to avoid overwrites
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        script_path = f"{job_name}_job_{job_num}_{timestamp}.sh"

        # Create script content
        script_content = create_sbatch_script(
            job_number=job_num,
            param_file=param_file,
            restart=restart,
            num_nodes=num_nodes,
            job_name=job_name,
            dependency=previous_job_id,
            account=account,
            cores_per_node=cores_per_node
        )

        # Write script to file
        with open(script_path, 'w') as f:
            f.write(script_content)

        # Submit job and capture job ID
        try:
            result = subprocess.run(
                ['sbatch', script_path],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True,
                check=True
            )
            # Extract job ID from sbatch output
            job_id = result.stdout.strip().split()[-1]
            previous_job_id = job_id
            print(f"Submitted {job_name}_{job_num} (Job ID: {job_id})")

        except subprocess.CalledProcessError as e:
            print(f"Error submitting {job_name}_{job_num}: {e}")
            return

if __name__ == "__main__":
    # Set up argument parser
    parser = argparse.ArgumentParser(description='Submit a chain of GIZMO simulation jobs to SLURM')
    parser.add_argument('--num-jobs', type=int, default=1,
                      help='Number of jobs to submit in the chain (default: 1)')
    parser.add_argument('--param-file', type=str, default='params.txt',
                      help='Parameter file for the GIZMO simulation (default: params.txt)')
    parser.add_argument('--num-nodes', type=int, default=1,
                      help='Number of nodes to request (default: 1)')
    parser.add_argument('--job-name', type=str, default='gizmo_sim',
                      help='Base name for the jobs (default: gizmo_sim)')
    parser.add_argument('--restart', type=int, choices=[1, 2],
                      help='Restart mode (1 or 2)')
    parser.add_argument('--initial-dependency', type=str,
                      help='Job ID for initial dependency (default: None)')
    parser.add_argument('--account', type=int, default=1, choices=[1, 2],
                      help='Account number (1 for rrg-matzner, 2 for rrg-murray-ac) (default: 1)')
    parser.add_argument('--cores-per-node', type=int, default=40,
                      help='Number of cores per node (default: 40)')

    # Parse arguments
    args = parser.parse_args()

    # Validate inputs
    if args.num_jobs < 1:
        raise ValueError("Number of jobs must be positive")
    if args.num_nodes < 1:
        raise ValueError("Number of nodes must be positive")
    if args.cores_per_node < 1:
        raise ValueError("Number of cores per node must be positive")
    if args.account not in [1, 2]:
        raise ValueError("Account must be either 1 (rrg-matzner) or 2 (rrg-murray-ac)")
    if not args.param_file:
        raise ValueError("Parameter file must be provided")
    if not args.job_name:
        raise ValueError("Job name must be provided")

    # Submit job chain
    if args.initial_dependency:
        submit_job_chain(args.num_jobs, args.param_file, args.restart, 
                        args.num_nodes, args.job_name, args.initial_dependency,
                        args.account, args.cores_per_node)
    else:
        submit_job_chain(args.num_jobs, args.param_file, args.restart, 
                        args.num_nodes, args.job_name, account=args.account,
                        cores_per_node=args.cores_per_node)
