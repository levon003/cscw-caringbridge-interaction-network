#!/bin/bash -l
#PBS -l walltime=40:00:00,nodes=1:ppn=8,mem=50gb
#PBS -m abe
#PBS -M eriks074@umn.edu
#PBS -N Caringbridge_Dyadic_Length
#PBS -o /home/srivbane/eriks074/repos/sna-social-support/dyad_growth/distributions.stdout
#PBS -e /home/srivbane/eriks074/repos/sna-social-support/dyad_growth/distributions.stderr

working_dir="/home/srivbane/eriks074/repos/sna-social-support/dyad_growth/"
cd $working_dir
echo "In '$working_dir', running the dyad length distribution script."
python3 distributions.py
echo "Finished."

