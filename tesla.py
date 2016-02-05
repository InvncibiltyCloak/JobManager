from bs4 import BeautifulSoup
import requests
from urllib import parse as urlparse
import sys

DETAIL_URL = 'https://chc.tbe.taleo.net/chc01/ats/careers/requisition.jsp?org=TESLA&cws=1&rid='

def scrape(chosen_ids):
    s = requests.Session()
    response = s.get('http://chc.tbe.taleo.net/chc01/ats/careers/jobSearch.jsp?org=TESLA&cws=1')

    soup = BeautifulSoup(response.text, 'html.parser')
    hidden_data = soup.find('form', attrs={'name':'TBE_theForm'}).find_all('input', type='hidden')
    post_data = {name: value for (name, value) in zip([e.get('name') for e in hidden_data], [e.get('value') for e in hidden_data])}

    post_data['CUSTOM_974'] = '2545' # Job category: Engineering
    post_data['location'] = [6, 7, 11, 12, 15, 16, 18, 21, 29, 35, 37, 44, 50, 
            51, 54, 56, 91, 92, 93, 95, 97, 98, 100, 101, 102, 105, 106, 107, 
            108, 109, 112, 113, 114, 115, 116, 117, 119, 121, 122, 124, 125, 
            126, 127, 128, 130, 131, 132, 133, 136, 137, 140, 142, 145, 146, 
            151, 152, 153, 156, 157, 159, 160, 161, 163, 164, 166, 167, 170, 
            174, 204, 206, 207, 209, 210, 211, 212, 216, 217, 218, 224, 228, 
            229, 230, 231, 232, 233, 235, 257, 258, 259, 260, 261, 263, 270, 
            271, 273, 274, 275, 303, 310, 311, 314, 315, 316, 318, 319, 325, 
            326, 327, 332, 337, 338, 340, 342, 343, 344, 346, 350, 351, 352, 
            353, 354, 355, 356, 357, 358, 359, 360, 361, 362, 370, 371, 372, 
            373, 374, 375, 376, 377, 378, 379, 380, 394, 395, 398, 400, 402, 
            403, 406, 409, 410, 412, 413, 414, 420, 422, 426] # Any location in NA

    response2 = s.post('http://chc.tbe.taleo.net/chc01/ats/careers/searchResults.jsp?org=TESLA&cws=1', data = post_data)

    response3 = s.get('http://chc.tbe.taleo.net/chc01/ats/careers/searchResults.jsp?org=TESLA&cws=1&act=sort&sortColumn=3')

    soup3 = BeautifulSoup(response3.text, 'html.parser')
    job_entries = soup3.find('table', id='cws-search-results').find_all('tr')[1:]

    parsed_entries = []
    for entry in job_entries:
        href = entry.a.get('href')
        query_dict = urlparse.parse_qs(urlparse.urlparse(href).query)
        ref_id = int(query_dict['rid'][0])
        
        title = entry.a.text
        
        parsed_entries.append((ref_id, title))

    parsed_entries.sort(reverse=True, key=lambda e: e[0])

    try:
        previous_job_file = open('tesla.txt','r')
        previous_job_ids = list(map(int, previous_job_file.readline().strip().split(',')))
        previous_job_file.close()
    except FileNotFoundError:
        previous_job_ids = []
     
        
    first = True
    for entry in parsed_entries:
        if entry[0] not in previous_job_ids:
            previous_job_ids.append(entry[0])
            if first:
                print("New jobs at Tesla:")
                first = False
            # Deal with some unicode issues here
            fixed = entry[1].encode(sys.stdout.encoding, errors='replace').decode(sys.stdout.encoding)
            print('\t' + fixed + ' - ' + str(entry[0]))
        if entry[0] in chosen_ids:
            os.system('firefox --new-tab ' + DETAIL_URL + str(entry[0]))
            
            
    previous_job_file = open('tesla.txt', 'w')
    previous_job_file.write(','.join(map(str, previous_job_ids)))
    previous_job_file.close()
    
if __name__ == '__main__':
    scrape()
