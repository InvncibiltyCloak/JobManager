from bs4 import BeautifulSoup
from urllib import request
import re
import os


def scrape(chosen_ids):
    response = request.urlopen('https://careers-cree.icims.com/jobs/search?in_iframe=1')
    soup = BeautifulSoup(response.readall(), 'html.parser')
    rows = soup.table.find_all('tr')
    
    try:
        previous_last_result = open('cree.txt','r').readline().strip()
    except FileNotFoundError:
        previous_last_result = ''
    
    new_postings = True
    first = True
    for row in rows[1:]:
        result = row.a['title'].strip()
        if result == previous_last_result:
            new_postings = False
        elif new_postings:
            if first:
                print('New Cree Postings:')
            print('\t' + result)
        
        if int(re.search(r'[0-9]+', result).group(0)) in chosen_ids:
            os.system("firefox --new-tab '" + row.a['href'] + "'")
       
    if new_postings:
        prev_storage = open('cree.txt','w')
        prev_storage.write(rows[1:2].a['title'].strip())
        prev_storage.close()
