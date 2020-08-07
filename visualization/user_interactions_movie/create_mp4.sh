#/bin/bash
# Creates an MP4 from 

output_filename="user_interactions_plot.mp4"
ffmpeg -y -r 15 -f image2 -s 1000x1000 -i frames/f%d.png -vcodec libx264 -crf 15 -pix_fmt yuv420p ${output_filename}
echo "Created movie '${output_filename}'."

# Generate a gif as well
# Currently commented out, since the GIF produced is unnecessary (and huge)
#gif_output_filename="user_interactions_plot.gif"
#convert -delay 10 -loop 0 $(ls -v frames/*.png) ${gif_output_filename}
#echo "Created gif '${gif_output_filename}'."

echo "Finished."

