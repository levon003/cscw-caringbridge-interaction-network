#!/bin/bash -l
#PBS -l walltime=11:00:00,nodes=1:ppn=8,mem=8gb
#PBS -m abe
#PBS -M levon003@umn.edu
#PBS -N CB_guestbook_geoIpLookup
#PBS -o /home/srivbane/shared/caringbridge/data/projects/sna-social-support/geo_data/lookup_guestbook_geo_data.stdout
#PBS -e /home/srivbane/shared/caringbridge/data/projects/sna-social-support/geo_data/lookup_guestbook_geo_data.stderr

working_dir="/home/srivbane/levon003/repos/sna-social-support/geographic_analysis"
cd $working_dir
echo "In '$working_dir', running script."
python lookup_guestbook_geo_data.py
echo "Finished."

