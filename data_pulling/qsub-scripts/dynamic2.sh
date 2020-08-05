#!/bin/bash -l
#PBS -l walltime=30:00:00,nodes=1:ppn=8,mem=4gb
#PBS -m abe
#PBS -M eriks074@umn.edu
#PBS -N CaringBridge_dynamic_data_retrieval
#PBS -o /home/srivbane/eriks074/sna-social-support/data_pulling/qsub-scripts/dyn2.stdout
#PBS -e /home/srivbane/eriks074/sna-social-support/data_pulling/qsub-scripts/dyn2.stderr

working_dir="/home/srivbane/eriks074/sna-social-support/data_pulling/qsub-scripts"
cd $working_dir
echo "In '$working_dir', running the pair script."
python3 dynamic_pairs.py
echo "Finished."
