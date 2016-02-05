import sys
import os

import requests
from bs4 import BeautifulSoup

SEARCH_URL = 'https://jobs.boeing.com/search-jobs/results?ActiveFacetID=6252001&CurrentPage=1&RecordsPerPage=10000&Distance=50&RadiusUnitType=0&Keywords=&Location=&Latitude=&Longitude=&ShowRadius=False&FacetTerm=&FacetType=0&FacetFilters[0].ID=6252001&FacetFilters[0].FacetType=2&FacetFilters[0].Count=515&FacetFilters[0].Display=United+States&FacetFilters[0].IsApplied=true&FacetFilters[0].FieldName=&SearchResultsModuleName=Search+Results&SearchFiltersModuleName=Search+Filters&SortCriteria=5&SortDirection=1&SearchType=5&CategoryFacetTerm=&CategoryFacetType=&LocationFacetTerm=&LocationFacetType=&KeywordType=&LocationType=&LocationPath=&OrganizationIds='

BASE_URL = 'https://jobs.boeing.com'

def scrape(chosen_ids):
    try:
        previous_job_file = open('boeing.txt','r')
        previous_job_ids = list(map(int, previous_job_file.readline().strip().split(',')))
        previous_job_file.close()
    except FileNotFoundError:
        previous_job_ids = []
    
    json = requests.get(SEARCH_URL).json()
    soup = BeautifulSoup(json['results'], 'html.parser')

    for job_html in soup.find('section', id='search-results').find_all('li')[1:]:
        rid = job_html.a['data-job-id']
        title = job_html.h2.text
        if int(rid) not in previous_job_ids:
            joined = title[:70] + ' - ' + rid
            fixed = joined.encode(sys.stdout.encoding, errors='replace').decode(sys.stdout.encoding)
            print('\t' + fixed)
            previous_job_ids.append(int(rid))
        if int(rid) in chosen_ids:
            os.system("firefox --new-tab '" + BASE_URL + job_html.a['href'] + "'")
        
    previous_job_file = open('boeing.txt', 'w')
    previous_job_file.write(','.join(map(str, previous_job_ids)))
    previous_job_file.close()

if __name__ == '__main__':
    scrape()

