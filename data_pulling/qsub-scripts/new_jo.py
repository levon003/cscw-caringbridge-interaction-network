import json
import numpy as np
import pandas as pd
from datetime import datetime
from IPython.display import display, clear_output
import csv as csv
import os
import subprocess

guestbook_fname = "/home/srivbane/shared/caringbridge/data/raw/guestbook_scrubbed.json"
journal_fname = "/home/srivbane/shared/caringbridge/data/raw/journal.json"
out_path = "/home/srivbane/shared/caringbridge/data/projects/sna-social-support/csv_data/"
chunk_size = 100000
allow = True

def main():
    header = ["userId", "siteId", "connectionType", "createdAt"]
    with open(journal_fname, encoding="utf-8") as infile:
        processed_count = 0;
        chunk_count = 0;
        jo = [];
        for line in infile:
            jo_json = json.loads(line)
            try:
                 jo.append((int(jo_json["userId"]), int(jo_json["siteId"]), "journal", int(jo_json["createdAt"]["$date"])))
            except KeyError:
                 pass
            finally:
                processed_count += 1
                if processed_count == chunk_size:
                    chunk_count += 1
                    clear_output(); display("" + str(chunk_count) + " chunks of " + str(chunk_size) + " processed.");           
                    processed_count = 0;
    with open(os.path.join(out_path, "jo.csv"), "w", encoding="utf-8") as outfile:
        j = pd.DataFrame(jo, columns = header);
        j = j.sort_values(by=["userId"]);
        j.to_csv(outfile, header=True, index=False)
    display("Finished!")

if __name__ == "__main__":
    main()
