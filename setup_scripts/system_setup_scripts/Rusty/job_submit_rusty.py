import subprocess
import os
from datetime import datetime
import argparse

def get_cpu_info(cpu_type):
    """
    Get CPU information based on CPU type.
    
    Args:
        cpu_type: Type of CPU to use
        
    Returns:
        tuple: (cores_per_node, constraint_flag)
    """
    cpu_map = {
        'genoa': (96, 'ib-genoa'),
        'icelake': (64, 'ib-icelake'), 
        'rome': (128, 'ib-rome'),
        'skylake': (36, 'ib-skylake'),
        'cascadelake': (96, 'ib-cascadelake'),
        'cooperlake': (192, 'ib-cooperlake')
    }
    
    if cpu_type not in cpu_map:
        raise ValueError(f"Unknown CPU type: {cpu_type}. Valid options: {list(cpu_map.keys())}")
    
    return cpu_map[cpu_type]

def create_sbatch_script(job_number, param_file, restart, num_nodes, job_name, dependency=None, partition="cca", cpu_type="rome", cores_per_node=None, wall_time=None):
    """
    Generate content for an sbatch script for GIZMO simulation on RUSTY system.

    Args:
        job_number: Number of the job in the sequence
        param_file: Parameter file for the GIZMO simulation
        restart: Integer indicating restart mode (1 or 2) or None for no flag
        num_nodes: Number of nodes requested
        job_name: Base name for the job
        dependency: Job ID this job depends on
        partition: Partition to use (cca or preempt, default: cca)
        cpu_type: Type of CPU to use (default: rome)
        cores_per_node: Number of cores per node (if None, uses CPU type default)
        wall_time: Wall time in hours (not used for RUSTY system)

    Returns:
        String containing the sbatch script content
    """
    # Get CPU constraint information
    cpu_cores, constraint = get_cpu_info(cpu_type)
    
    # Use specified cores_per_node or default from CPU type
    if cores_per_node is None:
        cores_per_node = cpu_cores
    
    num_cores = num_nodes * cores_per_node

    script = [
        "#!/bin/bash",
        f"#SBATCH -N{num_nodes} -C {constraint} -p {partition}",
        f"#SBATCH --job-name={job_name}_{job_number}"
    ]

    # Add preempt QoS if using preempt partition
    if partition == "preempt":
        script.append("#SBATCH --qos=preempt")

    if dependency:
        script.append(f"#SBATCH --dependency=afterany:{dependency}")

    script.extend([
        "",
        "module purge",
        "module load openmpi gsl fftw hdf5",
        "",
        "cd ../",
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
            f"python prep_restart.py {param_file}",
            ""
        ])

    # Build mpirun command
    mpirun_cmd = f"mpirun -np {num_cores} ./GIZMO {param_file}"
    if restart is not None:
        mpirun_cmd += f" {restart}"
    mpirun_cmd += " >\"$filename\" 2>gizmo.err"
    script.append(mpirun_cmd)

    return "\n".join(script)

def submit_job_chain(num_jobs, param_file, restart, num_nodes, job_name, \
                     initial_dependency=None, partition="cca", cpu_type="rome", cores_per_node=None, wall_time=None, new_sim=False):
    """
    Submit a chain of dependent GIZMO simulation jobs to SLURM on RUSTY system.

    Args:
        num_jobs: Number of jobs to submit in the chain
        param_file: Parameter file for the GIZMO simulation
        restart: Integer indicating restart mode (1 or 2) or None for no flag
        num_nodes: Number of nodes requested
        job_name: Base name for the job
        initial_dependency: Job ID that the first job in the chain should depend on
        partition: Partition to use (cca or preempt, default: cca)
        cpu_type: Type of CPU to use (default: rome)
        cores_per_node: Number of cores per node (if None, uses CPU type default)
        wall_time: Wall time in hours (not used for RUSTY system)
        new_sim: If True, first job will not use restart flag
    """
    previous_job_id = initial_dependency

    for job_num in range(1, num_jobs + 1):
        # Determine whether to use restart flag for this job
        current_restart = None if (new_sim and job_num == 1) else restart
        
        # Create script file with timestamp to avoid overwrites
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        script_path = f"{job_name}_job_{job_num}_{timestamp}.sh"

        # Create script content
        script_content = create_sbatch_script(
            job_number=job_num,
            param_file=param_file,
            restart=current_restart,
            num_nodes=num_nodes,
            job_name=job_name,
            dependency=previous_job_id,
            partition=partition,
            cpu_type=cpu_type,
            cores_per_node=cores_per_node,
            wall_time=wall_time
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
    parser.add_argument('--new-sim', action='store_true',
                      help='If set, first job will not use restart flag')
    parser.add_argument('--initial-dependency', type=str,
                      help='Job ID for initial dependency (default: None)')
    parser.add_argument('--partition', type=str, default='cca', choices=['cca', 'preempt'],
                      help='Partition to use (cca or preempt) (default: cca)')
    parser.add_argument('--cpu-type', type=str, default='rome', 
                      choices=['genoa', 'icelake', 'rome', 'skylake', 'cascadelake', 'cooperlake'],
                      help='CPU type to use (default: rome)')
    parser.add_argument('--cores-per-node', type=int, default=None,
                      help='Number of cores per node (if not specified, uses CPU type default)')
    parser.add_argument('--wall-time', type=float, default=None,
                      help='Wall time in hours (not used for RUSTY system)')

    # Parse arguments
    args = parser.parse_args()

    # Validate inputs
    if args.num_jobs < 1:
        raise ValueError("Number of jobs must be positive")
    if args.num_nodes < 1:
        raise ValueError("Number of nodes must be positive")
    if args.cores_per_node is not None and args.cores_per_node < 1:
        raise ValueError("Number of cores per node must be positive")
    if args.partition not in ['cca', 'preempt']:
        raise ValueError("Partition must be either 'cca' or 'preempt'")
    if args.cpu_type not in ['genoa', 'icelake', 'rome', 'skylake', 'cascadelake', 'cooperlake']:
        raise ValueError("Invalid CPU type")
    if not args.param_file:
        raise ValueError("Parameter file must be provided")
    if not args.job_name:
        raise ValueError("Job name must be provided")

    # Submit job chain
    if args.initial_dependency:
        submit_job_chain(args.num_jobs, args.param_file, args.restart, 
                        args.num_nodes, args.job_name, args.initial_dependency,
                        args.partition, args.cpu_type, args.cores_per_node, args.wall_time,
                        args.new_sim)
    else:
        submit_job_chain(args.num_jobs, args.param_file, args.restart, 
                        args.num_nodes, args.job_name, partition=args.partition,
                        cpu_type=args.cpu_type, cores_per_node=args.cores_per_node, wall_time=args.wall_time,
                        new_sim=args.new_sim)