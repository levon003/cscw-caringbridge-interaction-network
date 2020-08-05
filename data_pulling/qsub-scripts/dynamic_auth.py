import json 
import os
import sys
import csv as csv
import re
from tqdm import tqdm
import multiprocessing as mp

POISON = "POISON" # this is the kill switch for the write process
pwd = "/home/srivbane/shared/caringbridge/data/projects/sna-social-support/csv_data/"

def process_user(uid_lines, queue, uid):
    total_ints = 0
    first_int_createdAt = sys.maxsize;
    last_int_createdAt = -1
    for line in uid_lines:
        from_userId, siteId,  to_userId, connectionType, createdAt_str = line.split(",")
        assert uid ==  int(from_userId), "{} - {}".format(uid, from_userId)
        total_ints += 1
        createdAt = int(createdAt_str)
        if createdAt < first_int_createdAt:
            first_int_createdAt = createdAt
        if createdAt > last_int_createdAt:
            last_int_createdAt = createdAt
    output_tuple = (uid, total_ints, first_int_createdAt, last_int_createdAt)
    queue.put(output_tuple)

class WriterProcess(mp.Process):
    
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
                    uid, ti, fi, li = result
                    line = "{},{},{},{}\n".format(uid, ti, fi, li)
                    #t_uid, f_uid, fi, li, tg, ta, tr = result
                    #line = "{},{},{},{},{},{},{}\n".format(t_uid, f_uid, fi, li, tg, ta, tr)
                    outfile.write(line)
                except mp.TimeoutError:
                    sys.stderr.write("Process caused a timeout in mp.")

def process(inpath, outpath, max_res = None, line_lim = None):
    with mp.Pool(processes=24) as pool:
        results = []
        manager = mp.Manager()
        queue = manager.Queue()
        w_process = WriterProcess(outfile=outpath, queue=queue)
        w_process.start()
        print("Processes started.")
        f_uid = -1; t_uid = -1;
        with open(inpath, 'r', encoding='utf-8') as infile:
            uid_lines = []; pair_lines = [];
            for i, line in enumerate(infile):
                
                """ Both task one and task two are coded in """
                
                # TASK ONE
                tokens = line.split(",")
                if tokens[0] == "userId" or int(tokens[0]) == 0:
                    continue
                curr_uid = int(tokens[0])
                #if i % 10000 == 0:
                 #   print(i, f_uid, len(uid_lines))
                if f_uid != curr_uid:
                    if f_uid != -1:
                        result = pool.apply_async(process_user, (uid_lines, queue, f_uid,))
                        #Non-mp alternative: process_user(uid_lines, queue, f_uid)
                        results.append(result)
                    f_uid = curr_uid
                    uid_lines = []
                uid_lines.append(line)
                
                """
                # TASK TWO
                tokens = line.split(",")
                if tokens[0] == "from_userId" or int(tokens[0]) == 0 \
                or tokens[2] == "to_userId" or int(tokens[2]) == 0:
                    continue
                curr_fuid = int(tokens[0])
                curr_tuid = int(tokens[2])
                if i % 1000 == 1:
                    print(i, f_uid, t_uid, len(pair_lines))
                if f_uid != curr_fuid or t_uid != curr_tuid:
                    if f_uid != -1 and t_uid != -1:
                        result = pool.apply_async(process_pair, (pair_lines, queue, f_uid, t_uid,))
                        results.append(result)
                    f_uid = curr_fuid
                    t_uid = curr_tuid
                    pair_lines = []
                pair_lines.append(line)
            
                """
                """ End of modified code for task description """
                
                if max_res is not None and len(results) == max_res:
                    for result in tqdm(results, desc="Joining Results [Inner nest]"):
                        result.get()
                    results = []
                if line_lim is not None and i > line_lim:
                    break
                    
            """ Change this code for the function being processed """
            result = pool.apply_async(process_user, (uid_lines, queue, f_uid,))
            results.append(result)
            """ End of changed code for the multiprocessing fw"""
                    
        for result in tqdm(results, desc="Joining Results [Outer nest]"):
            result.get()
        
        queue.put(POISON)
        w_process.join()
        manager.shutdown()
    print("Finished!") 

def main():
    inpath = os.path.join(pwd, "jo.csv")
    outpath = os.path.join(pwd, "dynamic_auth.csv") # change based on task
    process(inpath, outpath, max_res = 1000000, line_lim = None)

if __name__ == "__main__":
    main()
