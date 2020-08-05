#!/usr/bin/env python3
# This script predicts author type for all journals (with some exceptions)
# It is the script form of content in the associated notebook.

import os
import re
import pandas as pd
import numpy as np

import sklearn
from sklearn.model_selection import train_test_split

from collections import Counter
import sqlite3
from nltk import word_tokenize
from html.parser import HTMLParser
from tqdm import tqdm
import random
import pickle
import datetime

from subprocess import Popen, PIPE
import sys
sys.path.append("/home/srivbane/levon003/repos/qual-health-journeys/annotation_data")
import journal as journal_utils

general_working_dir = "/home/srivbane/shared/caringbridge/data/projects/sna-social-support/author_type"
vw_working_dir = os.path.join(general_working_dir, "vw")
os.makedirs(vw_working_dir, exist_ok=True)
print(vw_working_dir)

vw_streaming_command = f"vw --quiet -i {vw_working_dir}/patient_authored.model -t -p /dev/stdout"
print(vw_streaming_command)

class MLStripper(HTMLParser):
    def __init__(self):
        super().__init__()
        self.reset()
        self.strict = False
        self.convert_charrefs = True
        self.fed = []
    def handle_data(self, d):
        self.fed.append(d)
    def get_data(self):
        return ''.join(self.fed)


def strip_tags(html_text):
    s = MLStripper()
    s.feed(html_text)
    return s.get_data()


def get_cleaned_text_from_token_list(token_list):
    cleaned_text = " ".join(token_list).replace(':', 'COLON').replace('|', 'PIPE').replace("\n", "NEWLINE ")
    return cleaned_text


def get_cleaned_text(text, strip_tags=True):
    if strip_tags:
        stripped = strip_tags(text)
    else:
        stripped = text
    tokens = word_tokenize(stripped)
    tokens = [token.lower() for token in tokens]
    cleaned_text = get_cleaned_text_from_token_list(tokens)
    return cleaned_text


def get_preds(results):
    # expects results of the form "0.564 sid912454joid5470dee0ca16b4c27bb0e9a5\n"
    preds = []
    try:
        for result in results:
            if result.strip() == '':
                continue
            pred, key = result.strip().split(" ")
            pred = float(pred)
            siteId, journalOid = key.split("joid")
            siteId = int(siteId[3:])
            pred_dict = {'author_type_raw_prediction': pred,
                         'site_id': siteId,
                         'journal_oid': journalOid}
            preds.append(pred_dict)
    except Exception as ex:
        print(ex)
        print("Potentially erroneous result:", result)
    return preds


def get_vw_format(journal):
    text = journal_utils.get_journal_text_representation(journal)
    if text is None:
        return None
    cleaned_text = get_cleaned_text(text, strip_tags=False)
    identifier = "sid%djoid%s" % (journal['site_id'], journal['journal_oid'])
    return " " + identifier + "|J " + cleaned_text + "\n"


def process_batch(batch_lines, vw_proc):
    for line in batch_lines:
        #print(line)
        vw_proc.stdin.write(line)
        vw_proc.stdin.flush()
    results = []
    for i in range(len(batch_lines)):
        result = vw_proc.stdout.readline()
        #print(result)
        if result == '':
            raise ValueError("Reached end of stdout, which is a surprise given that # inputs should == # outputs.")
        results.append(result)
    preds = get_preds(results)
    return preds


def write_preds(fd, preds):
    for p in preds:
        line = "{},{},{}\n".format(p['site_id'], p['journal_oid'], p['author_type_raw_prediction'])
        fd.write(line)

def stream_journals(preds_filepath):
    vw_proc = Popen(vw_streaming_command, 
                    shell=True, encoding='utf-8',
                    stdout=PIPE, stdin=PIPE, stderr=None)
    try:
        batch_size = 100
        batch_lines = []
        journal_iter = journal_utils.iter_journal_texts(limit=-1)
        estimated_length = 15327592  # total number of journals
        report_frequency = 100000
        lines_written = 0
        journals_iterated = 0
        with open(preds_filepath, 'w') as outfile:
            for i, journal in enumerate(journal_iter):
                journals_iterated += 1
                if i % report_frequency == 0:
                    print(i, "%.2f" % (i / estimated_length * 100), str(datetime.datetime.now()))
                line = get_vw_format(journal)
                if line is None:
                    continue
                batch_lines.append(line)
                if len(batch_lines) == batch_size:
                    batch_preds = process_batch(batch_lines, vw_proc)
                    write_preds(outfile, batch_preds)
                    lines_written += len(batch_lines)
                    batch_lines = []
            if len(batch_lines) > 0:
                batch_preds = process_batch(batch_lines, vw_proc)
                write_preds(outfile, batch_preds)
                lines_written += len(batch_lines)
            # outfile.flush()
        print("Finished writing out predictions. " + str(datetime.datetime.now()))
        print(f"Iterated {journals_iterated} journal updates and wrote {lines_written} of them ({lines_written / journals_iterated * 100:.2f}%)."
    finally:
        vw_proc.stdin.close()
        vw_proc.stdout.close()
        
if __name__ == "__main__":
    preds_filepath = os.path.join(vw_working_dir, "all_journal_preds.csv")
    stream_journals(preds_filepath)

