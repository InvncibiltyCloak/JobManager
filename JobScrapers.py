''' 
Scrape workflow:
Get job search page from base_url
    Construct correct url
    Add necessary parameters
    Get page
Parse page for job ids
    Parse correct tags
    Get title, ID and link
Open any chosen pages
    Match ID to parsed pages
    Open relevant links
Store previous
    Add to previous object
    Pickle it
Clear chosen
    Move to chosen.old
    Generate new skeleton chosen
Done

'''

from bs4 import BeautifulSoup
from requests import Session
import urllib.parse as url
import os
from shlex import quote
from DocInherit import doc_inherit
import shutil
import pickle
import warnings
from random import randint
import re
import json
import time

#---------------------------------------

class JobManager():
    '''Manages a set of job scrapers and coordinates them in their
    activities.'''
    
    def __init__(self, companies = None, open_command = None):
        if companies is not None:
            self.companies = companies
        else:
            self.companies = []
            
        if open_command is not None:
            self.open_command = open_command
        else:
            self.open_command = 'firefox --new-tab '
        
    def add_company(self, company):
        self.companies.append(company)
         
    def print_new_jobs(self):
        self._load_previous_jobs()
        for company in self.companies:
            try:
                company.set_previous_jobs(self.previous_jobs[str(company)])
            except KeyError:
                pass
                
            company.get_job_list()
            width = os.get_terminal_size().columns
            jobs = company.get_new_jobs()
            if len(jobs) > 0:
                print('New jobs for {:s}:'.format(str(company)))
                print('    ' + '\n    '.join([job.name[:width-(8+len(job.id))] +
                                              ' - ' + job.id for job in jobs]))
            company.jobs_now_old()
            
    def _load_previous_jobs(self):
        try:
            with open('previous_jobs.pkl','rb') as file:
                self.previous_jobs = pickle.load(file)
        except FileNotFoundError:
            self.previous_jobs = {}
        
    def open_chosen_jobs(self):
        name_ids = self._parse_chosen_jobids()
        company_names = [str(company) for company in self.companies]
        for chosen_name, jobids in name_ids.items():
            try:
                company = self.companies[company_names.index(chosen_name)]
                company.set_chosen_jobids(jobids)
                company.open_chosen_jobs(self.open_command)
            except ValueError:
                pass
            
        
        self._reset_chosen_jobids()
        
    def _parse_chosen_jobids(self):
        with open('chosen','r') as file:
            current_company = ''
            name_ids = {}
            for line in file:
                line.strip()
                if not line == '':
                    if line[0] == '[':
                        current_company = line.strip()[1:-1]
                    else:
                        try:
                            name_ids[current_company].append(line.strip())
                        except KeyError:
                            name_ids[current_company] = [line.strip()]
        return name_ids
        
    def _reset_chosen_jobids(self):
        if os.path.isfile('chosen'):
            shutil.copyfile('chosen', 'chosen.old')
        with open('chosen','w') as file:
            for company in self.companies:
                file.write('[' + str(company) + ']\n')
                
    def save_previous_jobs(self):
        for company in self.companies:
            self.previous_jobs[str(company)] = company.previous_jobs
            
        with open('previous_jobs.pkl','wb') as file:
            pickle.dump(self.previous_jobs, file)

#---------------------------------------

class Job():
    def __init__(self, name, req_id, url = None):
        self.name = name
        self.id = str(req_id)
        self.url = url
        
    def __str__(self):
        return self.name + ' - ' + self.id
        
    def __eq__(self, other):
        if other is self:
            return True
        else:
            return self.name == other.name and self.id == other.id
        
    def __hash__(self):
        return hash((self.name, self.id))

#---------------------------------------

class JobScraper():
    '''An abstract class which defines the interfaces for a generic job
    listing scraper.'''
    def __init__(self, company_name, base_url, search_params = None):
        self.company_name = company_name
        self.url = base_url
        
        if search_params is None:
            self.search_params = {}
        else:
            self.search_params = search_params
        
        self.session = Session()
        self.job_list = None
        self.previous_jobs = []
        self.chosen_jobs = []

    # Override get_job_list in subclasses
    def get_job_list(self):
        '''Fetches the list of jobs from the web server'''
        pass
        
    # Override job page opener if necessary
    def _open_job_page(self, job, command):
        '''Opens the job description page for a specific job.'''
#        print("Opening {} at {}".format(job.name, self.company_name))
#        print(job.url, end="")
        os.system(command + quote(job.url))
        
    # The below functions should not need to be overridden
    def _jobids_to_jobs(self, jobids):
        '''Converts a job id number to a Job object.'''
        posted_jobs = self.get_job_list()
        posted_jobids = [job.id for job in posted_jobs]
        jobs = []
        for jobid in jobids:
            try:
                jobs.append(posted_jobs[posted_jobids.index(jobid)])
            except ValueError:
                print('Warning: Unable to find job ' + jobid + ' for company ' + self.company_name)
                #jobs.append(Job('Unknown', jobid))
        return jobs
    
    def set_chosen_jobids(self, jobids):
        '''Sets a given list of jobids as the list of chosen jobs.'''
        if jobids is not None:
            self.chosen_jobs = self._jobids_to_jobs(jobids)
        else:
            self.chosen_jobs = []
        
    def add_chosen_jobids(self, jobids):
        '''Adds a given list of jobids to the list of chosen jobs.'''
        if jobids is not None:
            self.chosen_jobids += self._jobids_to_jobs(jobids)
    
    def set_previous_jobids(self, jobids):
        '''Sets a given list of jobids as the list of previous jobs.'''
        if jobids is not None:
            self.previous_jobs = self._jobids_to_jobs(jobids)
        else:
            self.previous_jobs = []
        
    def add_previous_jobids(self, jobids):
        '''Adds a given list of jobids to the list of previous jobs.'''
        if jobids is not None:
            self.previous_jobs += self._jobids_to_jobs(jobids)
        
    def set_chosen_jobs(self, jobs):
        '''Sets a given list of jobs as the list of chosen jobs.'''
        if jobs is not None:
            self.chosen_jobs = jobs
        else:
            self.chosen_jobs = []
        
    def add_chosen_jobs(self, jobs):
        '''Adds a given list of jobs to the list of chosen jobs.'''
        if jobs is not None:
            self.chosen_jobids += jobs
    
    def set_previous_jobs(self, jobs):
        '''Sets a given list of jobs as the list of previous jobs.'''
        if jobs is not None:
            self.previous_jobs = jobs
        else:
            self.previous_jobs = []
        
    def add_previous_jobs(self, jobs):
        '''Adds a given list of jobs to the list of previous jobs.'''
        if jobs is not None:
            self.previous_jobs += jobs
        
    def open_chosen_jobs(self, command):
        '''Opens all chosen jobs, by supplying the job details url to a given
        command.'''
        for job in self.chosen_jobs:
            self._open_job_page(job, command)
        
    def get_new_jobs(self):
        '''Returns a list of all jobs in job_list which are not in previous_jobs.'''
        if self.job_list is None:
            print('Warning: Job list for ' + self.company_name + ' is None.')
            return []
        else:
            return [job for job in self.job_list if job not in self.previous_jobs]
        
    def jobs_now_old(self):
        ''' Adds all current jobs to the previous_jobs list, declaring them to
        be old.'''
        self.previous_jobs = list(set(self.previous_jobs + self.job_list))
        
    def __str__(self):
        return self.company_name

#---------------------------------------

class TaleoScraper(JobScraper):
    '''Job scraper for Taleo based job boards. '''
    
    @doc_inherit
    def get_job_list(self):
        if self.job_list is None:
            SEARCH_MAGIC_PARAMS = {
                    'ftlcompclass': 'ButtonComponent',
                    'ftlinterfaceid': 'advancedSearchFooterInterface',
                    'ftlcompid': 'SEARCH',
                    'dropListSize':'1000' }
                    
            # Get base page
            response = self.session.get(self.url)
            
            # Determine result field structure
            soup = BeautifulSoup(response.text, 'lxml')
            scripts = soup.find_all('script', src=None)
            script_index = 0
            while '_ftl' not in scripts[script_index].text:
                script_index += 1
            script = scripts[script_index].text
            lines = script.split('\n')
            
            line_index = 0
            while not lines[line_index].strip().startswith('listRequisition'):
                line_index += 1
                
            while not lines[line_index].strip().startswith('_hlid'):
                line_index += 1
            
            line = lines[line_index]
            line = line.split(':')[1].strip()[:-1]
            array = eval(line)
            
            field_width = len(array)
            jobid_index = array.index('reqlistitem.no')
            title_index = array.index('reqlistitem.title')
            
            # Construct params
            soup = BeautifulSoup(response.text, 'lxml')
            self.base_paramset = {tag['name']:tag['value'] for tag in 
                    soup.find_all('input', type='hidden') if 'name' in tag.attrs}
            params = self.base_paramset.copy()
            params.update(self.search_params)
            params.update(SEARCH_MAGIC_PARAMS)
            
            # Generate POST request page name
            url_obj = list(url.urlparse(self.url))
            path = url_obj[2]
            filename, extension = os.path.splitext(path)
            extension = '.ajax'
            url_obj[2] = filename + extension
            ajax_url = url.urlunparse(url_obj)
            
            # Send POST request
            response = self.session.post(ajax_url, data=params)

            # Extract data from request
            soup = BeautifulSoup(response.text, 'lxml')
            raw_data = soup.p.text
            split = raw_data.split('!$!')[2].split('!|!')
            
            jobs = [list(split[i*field_width:(i+1)*field_width]) for i in
                    range(int(len(split)/field_width))]
            
            def gen_link(jobid):
                DETAIL_PAGE = '/jobdetail.ftl'
        
                # Generate URL
                url_obj = list(url.urlparse(self.url))
                url_obj[2] = os.path.split(url_obj[2])[0] + DETAIL_PAGE
                
                params = url.parse_qsl(url_obj[4])
                params.append(('job',jobid))
                url_obj[4] = url.urlencode(params, doseq=True)
                
                detail_url = url.urlunparse(url_obj)
                return detail_url
            
            # Store job info
            self.job_list = [Job(job[title_index], job[jobid_index],
                             url=gen_link(job[jobid_index])) for job in jobs]
        return self.job_list
        
#---------------------------------------

class OldTaleoScraper(JobScraper):
    '''Job scraper for older Taleo based job boards. You can tell the difference
    between new and old by the address. Old does not have company domain name.'''
    @doc_inherit
    def get_job_list(self):
        if self.job_list is None:
            # Exploit: sort by non-existant column to get all results per page
            EXPLOIT_PARAMS = {'act':'sort','sortColumn':'20'}
            RESULTS_PAGE = '/searchResults.jsp'
            # Get base page
            response = self.session.get(self.url)
            
            # Construct params
            soup = BeautifulSoup(response.text, 'html5lib')
            form = soup.find('form',attrs={'name':'TBE_theForm'})
            self.base_paramset = {tag['name']:tag['value'] for tag in 
                    form.find_all('input', type='hidden')}
            params = self.base_paramset.copy()
            params.update(self.search_params)
            
            # Generate POST request page name
            url_obj = list(url.urlparse(self.url))
            url_obj[2] = os.path.split(url_obj[2])[0] + RESULTS_PAGE
            results_url = url.urlunparse(url_obj)
            
            # Send requests
            response = self.session.post(results_url, data=params)
            response = self.session.get(results_url, params=EXPLOIT_PARAMS)

            # Extract data from request
            soup = BeautifulSoup(response.text, 'html5lib')
            rows = soup.find('table', id='cws-search-results').find_all('tr')[1:]
            
            def gen_link(jobid):
                DETAIL_PAGE = '/requisition.jsp'
        
                # Generate URL
                url_obj = list(url.urlparse(self.url))
                url_obj[2] = os.path.split(url_obj[2])[0] + DETAIL_PAGE

                params = url.parse_qsl(url_obj[4])
                params.append(('rid',jobid))
                url_obj[4] = url.urlencode(params, doseq=True)
                
                detail_url = url.urlunparse(url_obj)
                return detail_url
            
            
            self.job_list = []
            for row in rows:
                title = row.a.text
                query_string = url.urlparse(row.a['href'])[4]
                jobid = url.parse_qs(query_string)['rid'][0]
                self.job_list.append(Job(title, jobid, url=gen_link(jobid)))
                
        return self.job_list
        
#---------------------------------------
       
class ICIMSScraper(JobScraper):
    '''Generic scraper for ICIMS based job sites.'''
    @doc_inherit
    def get_job_list(self):
        if self.job_list is None:
            MAGIC_PARAMS = {'in_iframe':'1', 'mode':'redo', 'pr': 0, 
                    'schemaId':'$T{Job}.$T{JobPost}.$F{PostedDateTime}'}
                    
            # Construct params
            params = self.search_params.copy()
            params.update(MAGIC_PARAMS)
            
            # Get first results page
            response = self.session.get(self.url, params=params)
            soup = BeautifulSoup(response.text, 'lxml')
            job_table = soup.find('table', attrs={'class':'iCIMS_JobsTable'})
            has_more_pages = True
            
            self.job_list = []
            
            # Extract data from request and goto next page
            while has_more_pages:
                # Do extract jobs
                rows = job_table.find_all('tr')[1:]
                for row in rows:
                    cells = row.find_all('td')
                    for cell in cells:
                        cellType = cell.span.text.strip().lower()
                        if 'id' in cellType or '#' in cellType:
                            jobid = list(cell.stripped_strings)[1]
                        elif 'title' in cellType:
                            title = cell.a.text.strip()
                            url = cell.a['href']
#                    try:
                    self.job_list.append(Job(title, jobid, url=url))
#                    except UnboundLocalError:
#                        print('Warning: Couldnt find job title or id. '
#                                + self.company_name)
                    
                params['pr'] += 1
                
                # Get and check next page
                response = self.session.get(self.url, params=params)
                soup = BeautifulSoup(response.text, 'lxml')
                job_table = soup.find('table', attrs={'class':'iCIMS_JobsTable'})
                has_more_pages = job_table is not None
        
        return self.job_list
        
#---------------------------------------

class MyWorkdayJobsScraper(JobScraper):
    @doc_inherit
    def get_job_list(self):
        if self.job_list is None:
            last_page = False
            pagenum = 0
            self.job_list = []
            
            # Construct base link url
            url_obj = list(url.urlparse(self.url))
            url_obj[2] = ''
            base_link_url = url.urlunparse(url_obj)
            
            while not last_page:
                if pagenum == 0:
                    response = self.session.get(self.url + '/jobs', 
                            headers={'Accept':'application/json'})
                else:
                    response = self.session.get(self.url +
                            '/fs/searchPagination/searchJob/{:d}'.format(50*pagenum),
                            headers={'Accept':'application/json'})
                pagenum += 1
                json = response.json()
                body = json['body']['children']
                index = 0
                while body[index]['widget'] != 'facetSearchResult':
                    index += 1
                
                # Might be a problem if there are exactly 50 jobs in the results
                try:
                    if len(body[index]['children'][0]['listItems']) < 50:
                        last_page = True
                    
                    for job in body[index]['children'][0]['listItems']:
                        title = job['title']['instances'][0]['text']
                        link = base_link_url + job['title']['commandLink']
                        jobid = None
                        for subtitle in job['subtitles']:
                            if subtitle['ecid'] == 'monikerList.job.jobRequisitionId':
                                jobid = subtitle['instances'][0]['text']

                        self.job_list.append(Job(title, jobid, url=link))
                except KeyError: # No listItems, so no more jobs
                    last_page = True
                
        return self.job_list
        
#---------------------------------------

class SilkroadScraper(JobScraper):
    ''' '''
    def get_job_list(self, search_params):
        pass


#---------------------------------------

class JobviteHireScraper(JobScraper):
    '''For jobvite sites that start with hire.jobvite.com'''
    def get_job_list(self):
        if self.job_list is None:
            CSRF_URL = 'https://app.jobvite.com/admin/CsrfJavaScriptServlet'
            RESULTS_PAGE = '/CompanyJobsAPI.aspx'
            RESULTS_PARAM = {'command':'getcareerpage'}
            
            # Get base page
            response = self.session.get(self.url)
            
            # Get CSRF token
            csrf_page = self.session.get(CSRF_URL)
            csrf_injection = re.search(r'injectTokenForm\(this,(([^,)]+,?){3})\);', 
                    csrf_page.text)
            csrf_token = csrf_injection.group(1).split('"')[3]
            
            # Add CSRF and Content Type headers
            self.session.headers.update({'X-CSRF-TOKEN':csrf_token, 
                    'Content-Type':'text/plain;charset=UTF-8'})
            
            # Get other magic token
            soup = BeautifulSoup(response.text, 'lxml')
            scripts = soup.find_all('script', src=None)
            token_finder = re.compile(r'jvgetpage\(([^,)]+,){2}')
            for script in scripts:
                match = token_finder.search(script.text)
                if match is not None:
                    self.magic_token = match.group(1).split("'")[1]
                    
            # Extract company ID from base URL
            url_obj = list(url.urlparse(self.url))
            self.companyID = url.parse_qs(url_obj[4])['c'][0]
            
            # Construct url
            url_obj[2] = os.path.split(url_obj[2])[0] + RESULTS_PAGE
            url_obj[4] = url.urlencode(RESULTS_PARAM, doseq=True)
            request_url = url.urlunparse(url_obj)
            
            more_pages = True
            first_page = True
            self.job_list = []
            
            while more_pages:
                # Send POST request
                if first_page:
                    post_data = self._gen_postdata('F') # (F)irst page
                    first_page = False
                else:
                    post_data = self._gen_postdata('N') # (N)ext page
                response = self.session.post(request_url, data=post_data)
                soup = BeautifulSoup(response.text, 'lxml')
                
                #Determine page number
                paginate_label = soup.find('div',attrs={'class':'paginationLabel'})
                current_page = int(paginate_label.text.split()[0])
                total_pages = int(paginate_label.text.split()[2])
                if current_page < total_pages:
                    more_pages = True
                else:
                    more_pages = False
                    
                # Extract data from response
                table = soup.find(id='table_joblisting')
                rows = table.find_all('tr')[1:]
                
                # Link generator
                link_gen = self._joblink_factory(rows[0].a['href'].split("'")[1])
                
                # Store jobs
                for row in rows:
                    title = row.a.text.strip()
                    jobid = row.a['href'].split("'")[-2]
                    link = link_gen(jobid)
                    self.job_list.append(Job(title, jobid, url=link))
            
        return self.job_list
        
    def _joblink_factory(self, page):
        '''Returns a function which, when passed jobid, gives a link to the job'''
        url_obj = list(url.urlparse(self.url))
        params = url.parse_qs(url_obj[4])
        params.update({'page':page})
        def builder(jobid):
            p = params.copy()
            p.update({'j':jobid})
            url_obj[4] = url.urlencode(p, doseq=True)
            link = url.urlunparse(url_obj)
            return link
        return builder
        
    def _gen_postdata(self, pagemode):
        ''' Generates the text postdata for the weird jobvite format'''
        def item_or_empty(key):
            return self.search_params[key] if key in self.search_params else ''
        
        post_data = self.companyID + '\n'
        post_data += self.magic_token + '\n'
        post_data += '\n'
        post_data += 'SearchResults\n'
        post_data += '\n'
        post_data += 'main\n'
        post_data += 'jvpagemode=' + pagemode
        post_data += ',jvpagesize=30,jvretain=true,'
        post_data += 'jvdosearch=' + '1' if pagemode == 'F' else '0'
        post_data += ',jvkeywordsearch=' + item_or_empty('txtkeyword')
        post_data += ',jvCategory=' + item_or_empty('jvCategory')
        post_data += ',jvLocation=' + item_or_empty('jvLocation')
        post_data += ',jvrand=' + str(randint(0,111111)) + '\n'
        post_data += 'c=' + self.companyID + '\n'
        return post_data
#---------------------------------------

class JobviteJobsScraper(JobScraper):
    '''For jobvite sites that start with jobs.jobvite.com'''
    def get_job_list(self):
        pass
    
#---------------------------------------

class BrassringScraper(JobScraper):
    ''' '''
    def get_job_list(self):
        pass
    
#---------------------------------------

class DayforceHCMScraper(JobScraper):
    ''' '''
    def get_job_list(self):
        pass

#---------------------------------------

class ProfilsScraper(JobScraper):
    ''' '''
    def get_job_list(self):
        pass

#---------------------------------------

class EEaseScraper(JobScraper):
    ''' '''
    def get_job_list(self):
        pass

class MicrosoftScraper(JobScraper):
    '''For Microsoft careers'''
    def get_job_list(self):
        response = self.session.get(self.url)
        
        _ASYNCPOST = 'true'