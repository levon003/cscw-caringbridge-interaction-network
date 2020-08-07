#!/bin/bash -l
#PBS -l walltime=40:00:00,nodes=1:ppn=8,mem=4gb
#PBS -m abe
#PBS -M eriks074@umn.edu
#PBS -N CaringBridge_dynamic_sizing
#PBS -o /home/srivbane/eriks074/sna-social-support/data_pulling/qsub-scripts/size.stdout
#PBS -e /home/srivbane/eriks074/sna-social-support/data_pulling/qsub-scripts/size.stderr

working_dir="/home/srivbane/eriks074/sna-social-support/data_pulling/qsub-scripts"
cd $working_dir
echo "In '$working_dir', running the size script."
python3 nw_size.py
echo "Finished."
