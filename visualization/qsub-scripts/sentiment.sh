#!/bin/bash -l
#PBS -l walltime=40:00:00,nodes=1:ppn=8,mem=10gb
#PBS -m abe
#PBS -M eriks074@umn.edu
#PBS -N CaringBridge_user_sentiment_stuff
#PBS -o /home/srivbane/eriks074/sna-social-support/visualization/qsub-scripts/sent.stdout
#PBS -e /home/srivbane/eriks074/sna-social-support/visualization/qsub-scripts/sent.stderr

working_dir="/home/srivbane/eriks074/sna-social-support/visualization/qsub-scripts"
cd $working_dir
echo "In '$working_dir', running the sentiment script."
python3 sentiment.py
echo "Finished."
