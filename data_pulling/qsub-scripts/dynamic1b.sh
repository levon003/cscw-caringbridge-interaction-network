#!/bin/bash -l
#PBS -l walltime=40:00:00,nodes=1:ppn=8,mem=4gb
#PBS -m abe
#PBS -M eriks074@umn.edu
#PBS -N CaringBridge_dynamic_data_retrieval_b
#PBS -o /home/srivbane/eriks074/sna-social-support/data_pulling/qsub-scripts/dyn1b.stdout
#PBS -e /home/srivbane/eriks074/sna-social-support/data_pulling/qsub-scripts/dyn1b.stderr

working_dir="/home/srivbane/eriks074/sna-social-support/data_pulling/qsub-scripts"
cd $working_dir
echo "In '$working_dir', running the two python scripts."
python3 dynamic_auth.py
echo "Finished."
