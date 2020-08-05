#!/bin/bash -l
#PBS -l walltime=24:00:00,nodes=1:ppn=8,mem=4gb
#PBS -m abe
#PBS -M eriks074@umn.edu
#PBS -N CaringBridge_interaction_combine
#PBS -o /home/srivbane/eriks074/sna-social-support/data_pulling/qsub-scripts/ints.stdout
#PBS -e /home/srivbane/eriks074/sna-social-support/data_pulling/qsub-scripts/ints.stderr

working_dir="/home/srivbane/shared/caringbridge/data/projects/sna-social-support/csv_data"
cd $working_dir
echo "In '$working_dir', running sort."
sort -t"," -k1n,1 -o ints1.csv --parallel=24 ints.csv
echo "Finished."
