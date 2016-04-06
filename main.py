from JobScrapers import *

if __name__ == '__main__':
    manager = JobManager()  

    manager.add_company(OldTaleoScraper('Boeing I&A',
            'https://chk.tbe.taleo.net/chk01/ats/careers/jobSearch.jsp?org=VSICORP&cws=1'))
            
    manager.add_company(MyWorkdayJobsScraper('Silevo',
            'https://solarcity.wd1.myworkdayjobs.com/05'))
    
    manager.add_company(ICIMSScraper('Amazon',
            'https://us-amazon.icims.com/jobs/search',
            search_params = {'searchCategory':'30638'}))
            
    manager.add_company(OldTaleoScraper('Emerald Perf Matls',
            'http://chc.tbe.taleo.net/chc02/ats/careers/jobSearch.jsp?org=EMPERF&cws=1',
            search_params = {'CUSTOM_1042':[842,854]}))
            
    manager.add_company(ICIMSScraper('SunPower',
            'https://careers-sunpower.icims.com/jobs/search',
            search_params={'searchCategory':'8723'}))
            
    manager.add_company(ICIMSScraper('Solar World',
            'https://jobs-solarworld-usa.icims.com/jobs/search'))
    
    manager.add_company(JobviteHireScraper('SpaceX',
            'https://hire.jobvite.com/CompanyJobs/Careers.aspx?c=qz49Vfwr',
            search_params={'jvlocation':'Seattle, WA'}))
    
    manager.print_new_jobs()
    manager.open_chosen_jobs()
    manager.save_previous_jobs()
