#!/bin/bash 
#SBATCH --account=rrg-matzner
#SBATCH --nodes=12
#SBATCH --ntasks-per-node=40
#SBATCH --time=12:00:00
#SBATCH --job-name=original_split_sim
#SBATCH --output=mpi_output_%j.txt
#SBATCH --mail-type=FAIL

cd $SLURM_SUBMIT_DIR

#module load NiaEnv/2018a
#module load intel/2018.2
#module load intelmpi/2018.2
#module load gsl/2.4
#module load hdf5/1.8.20
#module load fftw-mpi/3.3.7

module load intel intelmpi gsl hdf5 fftw

mpirun -np 480 ./GIZMO params_splitting.txt 2 >gizmo.out
