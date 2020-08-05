#!/bin/bash -l
#PBS -l walltime=10:00:00,nodes=1:ppn=8,mem=22gb
#PBS -m abe
#PBS -M levon003@umn.edu
#PBS -N CaringBridge_mlogit_feature_extraction
#PBS -o /home/srivbane/shared/caringbridge/data/projects/sna-social-support/author_initiations/mlogitFeatureExtraction.stdout
#PBS -e /home/srivbane/shared/caringbridge/data/projects/sna-social-support/author_initiations/mlogitFeatureExtraction.stderr

working_dir="/home/srivbane/levon003/repos/sna-social-support/author_initiations"
cd $working_dir
echo "In '$working_dir', running script."
conda activate
python mlogitFeatureExtraction.py
echo "Finished (wrapper shell script)."

