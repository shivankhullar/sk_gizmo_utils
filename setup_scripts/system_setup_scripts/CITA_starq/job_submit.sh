#!/bin/bash -l
#PBS -l nodes=3:ppn=128
#PBS -l walltime=12:00:00
#PBS -r n
#PBS -j oe
#PBS -q starq

module purge
module load gcc/13.2.0 openmpi/4.1.6-gcc-ucx gsl/2.7.1 hdf5/1.12.1-ucx fftw/3.3.10-openmpi-ucx


# go to your working directory containing the batch script, code and data
cd $PBS_O_WORKDIR

make clean
make -j 20

export OMP_NUM_THREADS=2

#mpirun -np 128 ./GIZMO gizmo_parameters.txt > dummy.out
mpirun -np 192 -map-by node:SPAN ./GIZMO gizmo_parameters.txt 2
