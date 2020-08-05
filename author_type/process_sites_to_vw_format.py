#!/usr/bin/env python3
# Processes a list of site_ids into an unlabeled Vowpal Wabbit format where the only feature is the cleaned text of the journal body

import json
import os
import re
from tqdm import tqdm
from html.parser import HTMLParser
import multiprocessing as mp

import os
import re
import pandas as pd
import numpy as np
import sklearn
from collections import Counter
import sqlite3
from nltk import word_tokenize
from html.parser import HTMLParser
from tqdm import tqdm
import random
import pickle

POISON = "POISON"  # an object that is recognized as a "stop processing" signal by the writer process

DUMMY_JOURNAL = "This CaringBridge site was created just recently."


def get_db():
    journal_wd="/home/srivbane/shared/caringbridge/data/derived/sqlite"
    db_filename = os.path.join(journal_wd, "journal.db")
    db = sqlite3.connect(
            db_filename,
            detect_types=sqlite3.PARSE_DECLTYPES
        )
    db.row_factory = sqlite3.Row
    return db

        
def get_journal_texts(site_id):
    site_id = int(site_id)
    
    texts = []
    try:
        db = get_db()
        cursor = db.execute("""SELECT journal_oid, body
                                FROM journal 
                                WHERE site_id = ?""", 
                            (site_id,))
        results = cursor.fetchall()
        assert results is not None
        for result in results:
            body_text = result['body']
            if body_text is None:
                body_text = ""
            journal_oid = result['journal_oid']
            texts.append({
                'journal_oid': journal_oid,
                'body': body_text
            })
        return texts
    finally:
        db.close()

        
def get_cleaned_text_from_token_list(token_list):
    cleaned_text = " ".join(token_list).replace(':', 'COLON').replace('|', 'PIPE').replace("\n", "NEWLINE ")
    return cleaned_text


def get_cleaned_text(text):
    stripped = strip_tags(text)
    tokens = word_tokenize(stripped)
    tokens = [token.lower() for token in tokens]
    cleaned_text = get_cleaned_text_from_token_list(tokens)
    return cleaned_text


# See: https://stackoverflow.com/questions/753052/strip-html-from-strings-in-python
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


def strip_tags(html_text):  # this function strips HTML tags from a given text string
    s = MLStripper()
    s.feed(html_text)
    return s.get_data()


def process_site_id(queue, site_id):
    """
    This is the function that is called asyncronously.
    """
    body_list = get_journal_texts(site_id)
    for body in body_list:
        journal_oid = body['journal_oid']
        body_text = body['body']
        if len(body_text) < 50:
            continue
        if body_text.startswith(DUMMY_JOURNAL):
            continue
        cleaned_body = get_cleaned_text(body_text)

        identifier = "sid%djoid%s" % (site_id, journal_oid)
        formatted_journal = identifier + "|J " + cleaned_body
        
        line = formatted_journal + "\n"
        queue.put(line)

    
class WriterProcess(mp.Process):
    """
    WriterProcess writes received data to the given file.
    
    It is instantiated with a queue (that it reads from) and a filename (that it writes to).
    """
    def __init__(self, outfile, queue, **kwargs):
        super(WriterProcess, self).__init__()
        self.outfile = outfile
        self.queue = queue
        self.kwargs = kwargs

    def run(self):
        with open(self.outfile, 'w', encoding="utf-8") as outfile:
            while True:
                result = self.queue.get()
                if result == POISON:
                    break
                try:
                    outfile.write(result)
                except mp.TimeoutError:
                    sys.stderr.write("Timeout waiting for a process.\n")


def process_site_ids(site_ids, output_filepath, max_results=None, site_limit=None):
    """
    process_json_file starts a job for each of the given site_ids provided and calls a function asyncronously for each of them.
    
    :max_results: If provided, will clear the list of results after this number of jobs are requested
    :site_limit: If provided, only this number of sites will be read from the list. Useful for testing.
    """
    # we'll execute the processing of input in parallel, reducing the extracted
    # results back to a single writer process (which will write them to a file)
    with mp.Pool(processes=48) as pool:
        results = []
        manager = mp.Manager()
        result_queue = manager.Queue()
        writer_process = WriterProcess(outfile=output_filepath, queue=result_queue)
        writer_process.start()
        print ("Processes started.")
        for i, site_id in enumerate(site_ids):
            result = pool.apply_async(process_site_id, (result_queue, site_id,))
            results.append(result)
            if max_results is not None and len(results) == max_results:
                for result in tqdm(results, desc="Joining Results"):
                    result.get()
                results = []  # clear the list of results
            if site_limit is not None and i > site_limit:
                # done processing sites, break out of the async loop
                break
        
        # wait for all remaining tasks to terminate
        for result in tqdm(results, desc="Joining Results"):
            result.get()

        # Stop the writer process, ensuring that the queue has been fully processed
        result_queue.put(POISON)
        writer_process.join()
        manager.shutdown()
    print("Finished.")


def main():
    vw_working_dir = "/home/srivbane/shared/caringbridge/data/projects/qual-health-journeys/author_classification/vw"
    os.makedirs(vw_working_dir, exist_ok=True)
    unlabeled_vw_test_filepath = os.path.join(vw_working_dir, "unlabeled_candidate_sites.txt")
    print(f"Will write processed sites to '{unlabeled_vw_test_filepath}'.")
    
    candidate_site_working_dir = "/home/srivbane/shared/caringbridge/data/projects/qual-health-journeys/identify_candidate_sites"
    valid_sites_filename = os.path.join(candidate_site_working_dir, "valid_classification_sites.txt")
    with open(valid_sites_filename, 'r') as infile:
        candidate_site_ids = [int(line.strip()) for line in infile]
    assert len(candidate_site_ids) > 0
    print(f"Identified {len(candidate_site_ids)} to process into VW format.")
    
    process_site_ids(candidate_site_ids, unlabeled_vw_test_filepath, max_results=10000)


if __name__ == "__main__":
    main()

