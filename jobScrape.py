#! /usr/bin/python3
import sys
import os
import importlib

scripts = [file for file in os.listdir() if os.path.splitext(file)[1] == '.py' and os.path.isfile(file)]
scripts.remove('jobScrape.py')

try:
    chosen_job_file = open('chosen','r')
    lines = [line.strip() for line in chosen_job_file.readlines()]
except FileNotFoundError:
    previous_job_ids = []
finally:
    chosen_job_file.close()
    
chosen_ids = {}
employer = None
for line in lines:
    if '[' in line:
        employer = line[1:-1]
    else:
        try:
            chosen_ids[employer].append(int(line))
        except KeyError:
            chosen_ids[employer] = [int(line)]

employer_names = []
for script in scripts:
    module_name = os.path.splitext(script)[0]
    mod = importlib.import_module(module_name)
    
    try:
        results = mod.scrape(chosen_ids[module_name])
    except KeyError:
        results = mod.scrape([])
    
    employer_names.append('[' + module_name + ']')
    
os.system('mv chosen chosen.old')
chosen_file = open('chosen', 'w')
chosen_file.write('\n'.join(employer_names))
chosen_file.close()

    



