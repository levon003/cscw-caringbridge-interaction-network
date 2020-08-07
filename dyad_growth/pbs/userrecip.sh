#!/bin/bash -l
#PBS -l walltime=40:00:00,nodes=1:ppn=8,mem=50gb
#PBS -m abe
#PBS -M eriks074@umn.edu
#PBS -N Caringbridge_Dyadic_Length
#PBS -o /home/srivbane/eriks074/repos/sna-social-support/dyad_growth/pbs/recip.stdout
#PBS -e /home/srivbane/eriks074/repos/sna-social-support/dyad_growth/pbs/recip.stderr

working_dir="/home/srivbane/eriks074/repos/sna-social-support/dyad_growth/pbs/"
cd $working_dir
echo "In '$working_dir', running the recip script."
python3 userrecip.py
echo "Finished."

