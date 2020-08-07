#!/bin/bash -l
#PBS -l walltime=40:00:00,nodes=1:ppn=8,mem=10gb
#PBS -m abe
#PBS -M eriks074@umn.edu
#PBS -N CaringBridge_interactivity
#PBS -o /home/srivbane/eriks074/sna-social-support/visualization/qsub-scripts/inter.stdout
#PBS -e /home/srivbane/eriks074/sna-social-support/visualization/qsub-scripts/inter.stderr

working_dir="/home/srivbane/eriks074/sna-social-support/visualization/qsub-scripts"
cd $working_dir
echo "In '$working_dir', running the long interactivity gen script."
python3 inter.py
echo "Finished."
