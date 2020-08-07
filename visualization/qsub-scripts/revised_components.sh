#!/bin/bash -l
#PBS -l walltime=95:00:00,nodes=1:ppn=8,mem=150gb
#PBS -q ram256g
#PBS -m abe
#PBS -M eriks074@umn.edu
#PBS -N CaringBridge_SNA_Inds
#PBS -o /home/srivbane/eriks074/repos/sna-social-support/visualization/qsub-scripts/rc.stdout
#PBS -e /home/srivbane/eriks074/repos/sna-social-support/visualization/qsub-scripts/rc.stderr

working_dir="/home/srivbane/eriks074/repos/sna-social-support/visualization/qsub-scripts"
cd $working_dir
echo "In '$working_dir', running the graph generation script."
python3 revised_components.py
echo "Finished."
