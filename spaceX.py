from bs4 import BeautifulSoup
from urllib import request
import re
import os

def scrape(chosen_ids):
    response = request.urlopen('http://www.spacex.com/careers/list?type[]=20&type[]=37&type[]=53&location[]=54')
    soup = BeautifulSoup(response.readall(), 'html.parser')
    rows = soup.find_all('tr')[1:] # Remove first header row
    get_job_id = re.compile('/(\d+)$')
    try:
        previous_job_file = open('spaceX.txt','r')
        previous_job_ids = list(map(int, previous_job_file.readline().strip().split(',')))
        previous_job_file.close()
    except FileNotFoundError:
        previous_job_ids = []


    first = True

    for row in rows:
        curr_id = int(get_job_id.search(row.a['href']).group(1))
            if curr_id not in previous_job_ids:
                 previous_job_ids.append(curr_id)
                 if first:
                    print("New jobs at SpaceX:")
                    first = False
                 print('\t' + row.a.text + ' - ' + str(curr_id))
            if curr_id in chosen_ids:
                os.system('firefox --new-tab ' + row.a['href'])
         
    if not first: # There were new postings
      previous_job_file = open('spaceX.txt', 'w')
      previous_job_file.write(','.join(map(str, previous_job_ids)))
      previous_job_file.close()
         
   
