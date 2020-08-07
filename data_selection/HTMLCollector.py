#!/usr/bin/env python
# Script to generate HTML files of sites from an input list of site_ids

import requests
import time
import os

source = "/home/srivbane/shared/caringbridge/data/projects/sna-social-support/data_selection/human_site_annotation/random_site_ids_201910.txt"
cap = 1000  # only generate and output this number of sites listed in the input file, in the order they appear in the source input
update_limit = 3
port= 5000
output_dir = "/home/srivbane/shared/caringbridge/data/projects/sna-social-support/data_selection/human_site_annotation/html_random"

def main():
    ## Flask annotation web client must be running on the desired port number in order for this to work

    # Set an arbitrary high cap if no cap was set
    cap = 1000
    if cap is None:
        cap = 2**32

    # make sure the output directory exists
    os.makedirs(output_dir, exist_ok=True)

    # generate the HTML pages
    htmls = {}
    with open(source) as f:
        for i, line in enumerate(f):
            if i > cap:
                print(f"Generated {cap} sites, breaking.")
                break
                
            html = ""
            while html == "":
                try:
                    sid = int(line)
                    response = requests.get("http://127.0.0.1:{}/siteId/{}?update_limit={}".format(port, sid,
                                                                                               update_limit))
                    html_content = response.text
                    html = "OK"
                    htmls.update({sid: html_content})
                except Exception as ex:
                    print(ex)
                    print("Connection refused by the server. Retry...")
                    time.sleep(3)
                    #print("Retrying:")
                    #continue

    # Puts a bunch of html files into the specified output directory
    i = 0
    for sid, html in htmls.items():
        if i == cap:
            print("Limit reached.")
            break
        else:
            with open(os.path.join(output_dir, "site_{}.html".format(sid)), "w") as f:
                f.write(html + "\n");
            print("{}/{} created".format(i, cap));
        i += 1

if __name__ == "__main__":
    main()

