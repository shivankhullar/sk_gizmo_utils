#!/bin/bash
#SBATCH -J multi_refine
#SBATCH -p normal
#SBATCH -N 10
#SBATCH --ntasks-per-node 8
#SBATCH -t 02:00:00

export OMP_NUM_THREADS=7
source $HOME/.bashrc

module load intel/19 impi hdf5 fftw3 gsl
ibrun ./GIZMO ./params_splitting.txt 2 1>gizmo.out 2>gizmo.err


