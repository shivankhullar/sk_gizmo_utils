import subprocess
import os
from datetime import datetime
import argparse

def create_sbatch_script(job_number, param_file, restart, num_nodes, job_name, queue_name, ppn, dependency=None, wall_time=3):
    """
    Generate content for an sbatch script for GIZMO simulation.
    
    Args:
        job_number: Number of the job in the sequence
        param_file: Parameter file for the GIZMO simulation
        restart: Boolean indicating if the job should restart from a snapshot
        num_nodes: Number of nodes requested
        job_name: Base name for the job
        dependency: Job ID this job depends on
        wall_time: Wall time in hours (default: 3)
    """
    num_cores = num_nodes * ppn
    
    # Convert wall time to HH:MM:SS format
    hours = int(wall_time)
    minutes = int((wall_time - hours) * 60)
    seconds = int(((wall_time - hours) * 60 - minutes) * 60)
    wall_time_str = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
    
    script = [
        "#!/bin/bash -l",
        f"#PBS -l nodes={num_nodes}:ppn={ppn}",
        f"#PBS -l walltime={wall_time_str}",
        "#PBS -r n",
        "#PBS -j oe",
        f"#PBS -q {queue_name}",
        f"#PBS -N {job_name}_{job_number}",
    ]

    if dependency:
        #script.append(f"#SBATCH --dependency=afterany:{dependency}")
        script.append(f"#PBS -W depend=afterany:{dependency}")

    script.extend([
        "",
        "cd ${PBS_O_WORKDIR}",
        "",
        "module purge",
        "module load openmpi/4.1.6-gcc-ucx gsl/2.7.1 hdf5/1.12.1-ucx fftw/3.3.10-openmpi-ucx gcc/5.4.0",
        "export HDF5_DISABLE_VERSION_CHECK=1"
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
            "module load python/3.10.2",
            #"jargon",
            f"python prep_restart.py {param_file}",
            ""
        ])

    restart_flag = 2 if restart else 1
    if num_nodes>1:
        script.append(f"mpirun -np {num_cores} -map-by node:SPAN ./GIZMO {param_file} {restart_flag} >\"$filename\"")
    else:
        script.append(f"mpirun -np {num_cores} ./GIZMO {param_file} {restart_flag} >\"$filename\"")

    return "\n".join(script)

    

def submit_job_chain(num_jobs, param_file, restart, num_nodes, job_name, queue_name, ppn, initial_dependency=None, wall_time=3):
    """
    Submit a chain of dependent GIZMO simulation jobs to SLURM.
    
    Args:
        num_jobs: Number of jobs to submit in the chain
        param_file: Parameter file for the GIZMO simulation
        restart: Boolean indicating if the job should restart from a snapshot
        num_nodes: Number of nodes requested
        job_name: Base name for the job
        initial_dependency: Job ID that the first job in the chain should depend on
        wall_time: Wall time in hours (default: 3)
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
            queue_name=queue_name,
            ppn=ppn,
            dependency=previous_job_id,
            wall_time=wall_time
        )
        
        # Write script to file
        with open(script_path, 'w') as f:
            f.write(script_content)
        
        # Submit job and capture job ID
        try:
            result = subprocess.run(
                ['qsub', script_path],
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
    QUEUE_PPN_MAP = {
        "starq": 128,
        "greenq": 32,
        "sandyq": 16,
        "hpq": 16
    }

    # Set up argument parser
    parser = argparse.ArgumentParser(description='Submit a chain of GIZMO simulation jobs to CITA')
    parser.add_argument('--num-jobs', type=int, default=1,
                      help='Number of jobs to submit in the chain (default: 1)')
    parser.add_argument('--param-file', type=str, default='params.txt',
                      help='Parameter file for the GIZMO simulation (default: params.txt)')
    parser.add_argument('--job-name', type=str, default='gizmo_sim',
                      help='Base name for the jobs (default: gizmo_sim)')
    parser.add_argument('--queue', type=str, default='starq', choices=QUEUE_PPN_MAP.keys(),
                      help='Queue to submit to (starq/greenq/sandyq/hpq) (default: starq)')
    parser.add_argument('--num-nodes', type=int, default=1,
                      help='Number of nodes to request (default: 1)')
    parser.add_argument('--ppn', type=int,
                      help='Cores per node (default: queue-specific value)')
    parser.add_argument('--restart', type=int, choices=[1, 2],
                      help='Restart mode (1 or 2)')
    parser.add_argument('--initial-dependency', type=str,
                      help='Job ID for initial dependency (default: None)')
    parser.add_argument('--wall-time', type=float, default=3.0,
                      help='Wall time in hours (default: 24.0)')

    # Parse arguments
    args = parser.parse_args()

    # Validate inputs
    if args.num_jobs < 1:
        raise ValueError("Number of jobs must be positive")
    if args.num_nodes < 1:
        raise ValueError("Number of nodes must be positive")
    if not args.param_file:
        raise ValueError("Parameter file must be provided")
    if not args.job_name:
        raise ValueError("Job name must be provided")
    if args.queue not in QUEUE_PPN_MAP:
        raise ValueError("Invalid queue name")
    if args.wall_time <= 0:
        raise ValueError("Wall time must be positive")
    
    # Get PPN - use custom value if provided, otherwise use queue default
    ppn = args.ppn if args.ppn is not None else QUEUE_PPN_MAP[args.queue]
    if ppn < 1:
        raise ValueError("PPN must be positive")
    
    total_cores = args.num_nodes * ppn

    print(f"Selected queue: {args.queue}")
    print(f"Cores per node (ppn): {ppn}")
    print(f"Total cores requested: {total_cores}")

    # Submit job chain
    if args.initial_dependency:
        submit_job_chain(args.num_jobs, args.param_file, args.restart, 
                        args.num_nodes, args.job_name, args.queue, ppn, 
                        args.initial_dependency, args.wall_time)
    else:
        submit_job_chain(args.num_jobs, args.param_file, args.restart, 
                        args.num_nodes, args.job_name, args.queue, ppn,
                        wall_time=args.wall_time)



